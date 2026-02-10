import asyncio
import json
import logging
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .storage import load_config, save_config, normalize_config, apply_setpoints, apply_entities, apply_actuators
from .ha_client import HAClient
from .logic import compute_decision

def _read_app_version() -> str:
    path = Path("/app/config.yaml")
    if not path.exists():
        return "0.0.0"
    try:
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("version:"):
                return line.split(":", 1)[1].strip().strip('"').strip("'")
    except Exception:
        pass
    return "0.0.0"

APP_VERSION = _read_app_version()
app = FastAPI(title="e-ThermoMind", version=APP_VERSION)
ha = HAClient()
cfg = load_config()
ws_task: asyncio.Task | None = None
off_deadline: dict[str, float] = {"r22": 0.0, "r23": 0.0, "r24": 0.0}
action_log: list[str] = []
entity_icon_map: dict[str, str] = {}
last_dry_run_signature: str | None = None
recent_ui_actuations: dict[str, float] = {}
pending_auto_off: dict[str, asyncio.Task] = {}
transfer_tasks: dict[str, asyncio.Task] = {}
transfer_desired: dict[str, bool] = {}
manual_overrides: dict[str, bool] = {}
solar_night_state: bool | None = None
solar_night_last_change: float = 0.0
ws_clients: set[WebSocket] = set()

@app.on_event("startup")
async def on_startup():
    global cfg
    global ws_task
    cfg = load_config()
    logging.basicConfig(
        level=str(cfg.get("log_level", "info")).upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    await ha.start()
    ha.set_state_callback(_on_state_changed)
    if ha.enabled:
        ws_task = asyncio.create_task(ha.run())
        asyncio.create_task(_refresh_entity_registry_loop())

@app.on_event("shutdown")
async def on_shutdown():
    global ws_task
    if ws_task:
        ws_task.cancel()
    await ha.close()

async def _refresh_entity_registry_loop():
    if not ha.enabled:
        return
    while True:
        try:
            async with ha._session.get(f"{ha._http_url}/config/entity_registry/list") as r:
                if r.status == 200:
                    data = await r.json()
                    entity_icon_map.clear()
                    for item in data:
                        eid = item.get("entity_id")
                        icon = item.get("icon")
                        if eid and icon:
                            entity_icon_map[eid] = icon
        except Exception:
            pass
        await asyncio.sleep(60)

app.mount("/assets", StaticFiles(directory="/app/static/assets"), name="assets")

@app.get("/", response_class=HTMLResponse)
async def ui():
    with open("/app/static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())

@app.get("/api/config")
async def get_config():
    return JSONResponse(cfg)

@app.post("/api/config")
async def set_config(payload: dict):
    global cfg
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")
    cfg = normalize_config(payload)
    save_config(cfg)
    return JSONResponse({"ok": True})

@app.get("/api/decision")
async def decision():
    data = compute_decision(cfg, ha.states)
    await _apply_resistance_live(data)
    await _apply_transfer_live(data)
    await _apply_solar_live(data)
    await _apply_impianto_live()
    return JSONResponse(data)



def _state_is_on(entity_id: str | None) -> bool:
    if not entity_id:
        return False
    val = ha.states.get(entity_id, {}).get("state")
    if val is None:
        return False
    sval = str(val).strip().lower()
    return sval in ("on", "true", "1", "yes", "heat", "heating")
def _get_state(entity_id: str | None) -> str | None:
    if not entity_id:
        return None
    return ha.states.get(entity_id, {}).get("state")

async def _build_snapshot() -> dict:
    data = compute_decision(cfg, ha.states)
    await _apply_resistance_live(data)
    await _apply_transfer_live(data)
    await _apply_solar_live(data)
    await _apply_impianto_live()
    act = {}
    for k, eid in (cfg.get("actuators", {}) or {}).items():
        if eid:
            st = ha.states.get(eid, {})
            act[k] = {
                "entity_id": eid,
                "state": st.get("state"),
                "attributes": st.get("attributes", {}),
                "icon": entity_icon_map.get(eid)
            }
        else:
            act[k] = {"entity_id": None, "state": None, "attributes": {}, "icon": None}
    ent = {}
    for k, eid in (cfg.get("entities", {}) or {}).items():
        if eid:
            st = ha.states.get(eid, {})
            ent[k] = {
                "entity_id": eid,
                "state": st.get("state"),
                "attributes": st.get("attributes", {}),
                "icon": entity_icon_map.get(eid)
            }
        else:
            ent[k] = {"entity_id": None, "state": None, "attributes": {}, "icon": None}
    return {
        "decision": data,
        "status": {
            "ha_connected": bool(ha.enabled),
            "token_source": getattr(ha, "token_source", None),
            "version": APP_VERSION,
            "runtime_mode": cfg.get("runtime", {}).get("mode", "dry-run"),
        },
        "actions": action_log[-50:],
        "actuators": act,
        "entities": ent,
        "modules": cfg.get("modules_enabled", {}),
    }

def _actuator_key_for_entity(entity_id: str) -> str | None:
    for key, eid in (cfg.get("actuators", {}) or {}).items():
        if eid == entity_id:
            return key
    return None

def _module_for_actuator_key(key: str) -> str | None:
    if "resistenza" in key:
        return "resistenze_volano"
    if "impianto" in key or "comparto" in key or "mandata" in key:
        return "impianto"
    if "solare" in key or "ritorno_solare" in key:
        return "solare"
    if "miscelatrice" in key:
        return "miscelatrice"
    if "puffer_to_acs" in key:
        return "puffer_to_acs"
    if "pdc" in key or "antigelo" in key or "comparto_pdc" in key:
        return "pdc"
    return None

def _is_recent_ui(entity_id: str, window_s: float = 4.0) -> bool:
    ts = recent_ui_actuations.get(entity_id)
    if not ts:
        return False
    if time.time() - ts > window_s:
        recent_ui_actuations.pop(entity_id, None)
        return False
    return True

def _is_manual(entity_id: str | None) -> bool:
    if not entity_id:
        return False
    return bool(manual_overrides.get(entity_id))

async def _auto_off_after_delay(entity_id: str, module_key: str | None) -> None:
    try:
        await asyncio.sleep(2)
        if _is_recent_ui(entity_id):
            return
        current = _get_state(entity_id)
        if current != "on":
            return
        if module_key and not cfg.get("modules_enabled", {}).get(module_key, True):
            return
        await ha.call_service(entity_id, "off")
        action_log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} AUTO-OFF {entity_id} (HA manual guard)")
    finally:
        pending_auto_off.pop(entity_id, None)

async def _on_state_changed(entity_id: str, new_state: dict) -> None:
    if not entity_id or not isinstance(new_state, dict):
        return
    if new_state.get("state") != "on":
        return
    if _is_recent_ui(entity_id):
        return
    if _is_manual(entity_id):
        return
    key = _actuator_key_for_entity(entity_id)
    if not key:
        return
    module_key = _module_for_actuator_key(key)
    if module_key and not cfg.get("modules_enabled", {}).get(module_key, True):
        return
    # Se non appartiene a nessun modulo, lascialo manuale (no auto-off)
    if module_key is None:
        return
    if entity_id in pending_auto_off:
        return
    pending_auto_off[entity_id] = asyncio.create_task(_auto_off_after_delay(entity_id, module_key))

def _log_dry_run(decision_data: dict) -> None:
    global last_dry_run_signature
    step = int(decision_data.get("computed", {}).get("resistance_step", 0))
    export_w = decision_data.get("inputs", {}).get("grid_export_w")
    dest = decision_data.get("computed", {}).get("dest")
    source = decision_data.get("computed", {}).get("source_to_acs")
    act = cfg.get("actuators", {})
    flags = decision_data.get("computed", {}).get("flags", {})
    modules = cfg.get("modules_enabled", {})
    r22 = act.get("r22_resistenza_1_volano_pdc")
    r23 = act.get("r23_resistenza_2_volano_pdc")
    r24 = act.get("r24_resistenza_3_volano_pdc")
    rg = act.get("generale_resistenze_volano_pdc")
    want = {
        "R22": "ON" if step >= 1 else "OFF",
        "R23": "ON" if step >= 2 else "OFF",
        "R24": "ON" if step >= 3 else "OFF",
        "RG": "ON" if step >= 1 else "OFF",
    }
    notes: list[str] = []
    def _mod_state(key: str, active: bool, has_logic: bool = True) -> str:
        if not modules.get(key, True):
            return "DISABLED"
        if not has_logic:
            notes.append(key)
            return "OFF"
        return "ON" if active else "OFF"

    res_module = "DISABLED"
    if modules.get("resistenze_volano", True):
        res_module = f"STEP {step}"

    module_states = {
        "resistenze_volano": res_module,
        "volano_to_acs": _mod_state("volano_to_acs", bool(flags.get("volano_to_acs"))),
        "volano_to_puffer": _mod_state("volano_to_puffer", bool(flags.get("volano_to_puffer"))),
        "puffer_to_acs": _mod_state("puffer_to_acs", bool(flags.get("puffer_to_acs"))),
        "solare": _mod_state("solare", bool(flags.get("solare_to_acs"))),
        "miscelatrice": _mod_state("miscelatrice", False, has_logic=False),
        "pdc": _mod_state("pdc", False, has_logic=False)
    }

    signature = json.dumps({
        "dest": dest,
        "source": source,
        "export_w": export_w,
        "step": step,
        "modules": module_states,
        "want": want
    }, sort_keys=True)
    if signature == last_dry_run_signature:
        return
    last_dry_run_signature = signature
    action_log.append(
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} DRY-RUN dest={dest} source={source} "
        f"export={export_w}W step={step}"
    )
    action_log.append(
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} DRY-RUN would set "
        f"{want['RG']} {rg} | {want['R22']} {r22} | {want['R23']} {r23} | {want['R24']} {r24}"
    )
    action_log.append(
        f"{time.strftime('%Y-%m-%d %H:%M:%S')} DRY-RUN modules "
        f"resistenze_volano={module_states['resistenze_volano']}, "
        f"volano_to_acs={module_states['volano_to_acs']}, "
        f"volano_to_puffer={module_states['volano_to_puffer']}, "
        f"puffer_to_acs={module_states['puffer_to_acs']}, "
        f"solare={module_states['solare']}, "
        f"miscelatrice={module_states['miscelatrice']}, "
        f"pdc={module_states['pdc']}"
    )
    if notes:
        action_log.append(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')} DRY-RUN note: no logic for {', '.join(notes)}"
        )

async def _set_resistance(entity_id: str | None, want_on: bool) -> None:
    if not entity_id or not ha.enabled:
        return
    if _is_manual(entity_id):
        return
    current = _get_state(entity_id)
    if want_on and current != "on":
        recent_ui_actuations[entity_id] = time.time()
        await ha.call_service(entity_id, "on")
        action_log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} ON {entity_id}")
    if (not want_on) and current != "off":
        recent_ui_actuations[entity_id] = time.time()
        await ha.call_service(entity_id, "off")
        action_log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} OFF {entity_id}")

async def _set_actuator(entity_id: str | None, want_on: bool) -> None:
    if not entity_id or not ha.enabled:
        return
    if _is_manual(entity_id):
        return
    current = _get_state(entity_id)
    if want_on and current != "on":
        recent_ui_actuations[entity_id] = time.time()
        await ha.call_service(entity_id, "on")
        action_log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} ON {entity_id}")
    if (not want_on) and current != "off":
        recent_ui_actuations[entity_id] = time.time()
        await ha.call_service(entity_id, "off")
        action_log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} OFF {entity_id}")

def _sun_is_night() -> bool | None:
    st = ha.states.get("sun.sun", {})
    state = st.get("state")
    if state == "below_horizon":
        return True
    if state == "above_horizon":
        return False
    return None

def _solar_night_debounced() -> bool:
    global solar_night_state, solar_night_last_change
    now = time.time()
    sol_cfg = cfg.get("solare", {})
    pv_entity = sol_cfg.get("pv_entity", "")
    pv_day = float(sol_cfg.get("pv_day_w", 1000.0))
    pv_night = float(sol_cfg.get("pv_night_w", 300.0))
    debounce_s = float(sol_cfg.get("pv_debounce_s", 300))

    desired = None
    if pv_entity:
        try:
            pv_val = float(ha.states.get(pv_entity, {}).get("state"))
        except Exception:
            pv_val = None
        if pv_val is not None:
            if solar_night_state is None:
                desired = pv_val < pv_night
            else:
                if solar_night_state:
                    desired = pv_val < pv_day
                else:
                    desired = pv_val < pv_night
    if desired is None:
        desired = _sun_is_night()
    if desired is None:
        # keep last if unknown
        return bool(solar_night_state)
    if solar_night_state is None:
        solar_night_state = desired
        solar_night_last_change = now
        return desired
    if desired != solar_night_state and (now - solar_night_last_change) < debounce_s:
        return solar_night_state
    if desired != solar_night_state:
        solar_night_state = desired
        solar_night_last_change = now
    return solar_night_state

def _cancel_transfer_task(key: str) -> None:
    task = transfer_tasks.pop(key, None)
    if task:
        task.cancel()

async def _delayed_actuate(task_key: str, entity_id: str, want_on: bool, delay_s: float) -> None:
    try:
        await asyncio.sleep(max(0.0, delay_s))
        await _set_actuator(entity_id, want_on)
    finally:
        transfer_tasks.pop(task_key, None)

async def _set_transfer_pair(
    name: str,
    valve_eid: str | None,
    pump_eid: str | None,
    want_on: bool,
    start_s: float,
    stop_s: float,
) -> None:
    prev = transfer_desired.get(name)
    transfer_desired[name] = want_on
    if want_on:
        await _set_actuator(valve_eid, True)
        if pump_eid and _get_state(pump_eid) != "on":
            if prev is False:
                _cancel_transfer_task(f"{name}:pump_off")
            if f"{name}:pump_on" not in transfer_tasks:
                transfer_tasks[f"{name}:pump_on"] = asyncio.create_task(
                    _delayed_actuate(f"{name}:pump_on", pump_eid, True, start_s)
                )
    else:
        await _set_actuator(valve_eid, False)
        if pump_eid and _get_state(pump_eid) != "off":
            if prev is True:
                _cancel_transfer_task(f"{name}:pump_on")
            if f"{name}:pump_off" not in transfer_tasks:
                transfer_tasks[f"{name}:pump_off"] = asyncio.create_task(
                    _delayed_actuate(f"{name}:pump_off", pump_eid, False, stop_s)
                )

async def _set_pump_only(name: str, pump_eid: str | None, want_on: bool) -> None:
    prev = transfer_desired.get(name)
    transfer_desired[name] = want_on
    if prev is not None and prev == want_on:
        await _set_actuator(pump_eid, want_on)
        return
    _cancel_transfer_task(f"{name}:pump_on")
    _cancel_transfer_task(f"{name}:pump_off")
    await _set_actuator(pump_eid, want_on)

async def _set_valve_only(valve_eid: str | None, want_on: bool) -> None:
    await _set_actuator(valve_eid, want_on)

async def _apply_resistance_live(decision_data: dict) -> None:
    if cfg.get("runtime", {}).get("mode") != "live":
        _log_dry_run(decision_data)
        return
    if not cfg.get("modules_enabled", {}).get("resistenze_volano", True):
        return
    act = cfg.get("actuators", {})
    r22 = act.get("r22_resistenza_1_volano_pdc")
    r23 = act.get("r23_resistenza_2_volano_pdc")
    r24 = act.get("r24_resistenza_3_volano_pdc")
    rg = act.get("generale_resistenze_volano_pdc")
    step = int(decision_data.get("computed", {}).get("resistance_step", 0))

    desired = {
        "r22": step >= 1,
        "r23": step >= 2,
        "r24": step >= 3,
    }

    off_delay = int(cfg.get("resistance", {}).get("off_delay_s", 5))
    now = time.time()

    for key, ent in (("r22", r22), ("r23", r23), ("r24", r24)):
        want_on = desired[key]
        current = _get_state(ent)
        if want_on:
            off_deadline[key] = 0.0
            if current != "on":
                await _set_resistance(ent, True)
        else:
            if current == "on":
                if off_deadline[key] == 0.0:
                    off_deadline[key] = now + off_delay
                elif now >= off_deadline[key]:
                    await _set_resistance(ent, False)
                    off_deadline[key] = 0.0
            else:
                off_deadline[key] = 0.0

    if rg:
        want_general = step >= 1
        await _set_resistance(rg, want_general)

async def _apply_transfer_live(decision_data: dict) -> None:
    if cfg.get("runtime", {}).get("mode") != "live":
        return
    if not ha.enabled:
        return

    flags = decision_data.get("computed", {}).get("flags", {})
    modules = cfg.get("modules_enabled", {})
    act = cfg.get("actuators", {})

    want_vol_acs = bool(flags.get("volano_to_acs")) and modules.get("volano_to_acs", True)
    want_vol_puf = bool(flags.get("volano_to_puffer")) and modules.get("volano_to_puffer", True)
    want_puf_acs = bool(flags.get("puffer_to_acs")) and modules.get("puffer_to_acs", True)

    if want_vol_acs:
        want_vol_puf = False
        want_puf_acs = False

    r6 = act.get("r6_valve_pdc_to_integrazione_acs")
    r7 = act.get("r7_valve_pdc_to_integrazione_puffer")
    r13 = act.get("r13_pump_pdc_to_acs_puffer")

    timers = cfg.get("timers", {})
    vta_start = float(timers.get("volano_to_acs_start_s", 5))
    vta_stop = float(timers.get("volano_to_acs_stop_s", 2))
    vtp_start = float(timers.get("volano_to_puffer_start_s", 5))
    vtp_stop = float(timers.get("volano_to_puffer_stop_s", 2))

    if want_vol_acs:
        await _set_transfer_pair("volano_to_acs", r6, r13, True, vta_start, vta_stop)
        await _set_valve_only(r7, False)
    elif want_vol_puf:
        await _set_valve_only(r6, False)
        await _set_transfer_pair("volano_to_puffer", r7, r13, True, vtp_start, vtp_stop)
    else:
        await _set_transfer_pair("volano_to_acs", r6, r13, False, vta_start, vta_stop)
        await _set_transfer_pair("volano_to_puffer", r7, r13, False, vtp_start, vtp_stop)

    await _set_pump_only(
        "puffer_to_acs",
        act.get("r14_pump_puffer_to_acs"),
        want_puf_acs,
    )

async def _apply_solar_live(decision_data: dict) -> None:
    if cfg.get("runtime", {}).get("mode") != "live":
        return
    if not ha.enabled:
        return
    if not cfg.get("modules_enabled", {}).get("solare", True):
        return

    sol_cfg = cfg.get("solare", {})
    mode = sol_cfg.get("mode", "auto")
    night = (mode == "night") or (mode == "auto" and _solar_night_debounced())

    act = cfg.get("actuators", {})
    r8 = act.get("r8_valve_solare_notte_low_temp")
    r9 = act.get("r9_valve_solare_normal_funz")
    r10 = act.get("r10_valve_solare_precedenza_acs")

    # R8/R9/R10 non devono restare in manuale: forza auto
    for eid in (r8, r9, r10):
        if eid:
            manual_overrides.pop(eid, None)

    # Cutback: se ACS o solare troppo caldi
    ent = cfg.get("entities", {})
    t_acs = ha.states.get(ent.get("t_acs"), {}).get("state")
    t_sol = ha.states.get(ent.get("t_solare_mandata"), {}).get("state")
    try:
        t_acs = float(t_acs)
    except Exception:
        t_acs = None
    try:
        t_sol = float(t_sol)
    except Exception:
        t_sol = None
    acs_max = float(cfg.get("acs", {}).get("max_c", 60.0))
    sol_max = float(sol_cfg.get("max_c", 90.0))
    cutback = (t_acs is not None and t_acs >= acs_max) or (t_sol is not None and t_sol >= sol_max)

    # R10: precedenza ACS quando solare attivo e non in cutback (vale anche di notte)
    solar_active = decision_data.get("computed", {}).get("source_to_acs") == "SOLAR"
    r10_on = bool(solar_active and (not cutback))
    await _set_actuator(r10, r10_on)

    # R8/R9: mai tutte chiuse. Se R10 ON, R8 e R9 devono essere OFF.
    if r10_on:
        await _set_actuator(r8, False)
        await _set_actuator(r9, False)
    elif night:
        await _set_actuator(r8, True)
        await _set_actuator(r9, False)
    else:
        await _set_actuator(r8, False)
        await _set_actuator(r9, True)

async def _set_climate_hvac_mode(entity_id: str | None, mode: str) -> None:
    if not entity_id or not ha.enabled:
        return
    current = _get_state(entity_id)
    if current == mode:
        return
    await ha.call_service_named("climate", "set_hvac_mode", {"entity_id": entity_id, "hvac_mode": mode})
    action_log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} HVAC {entity_id} -> {mode}")

async def _set_input_select(entity_id: str | None, option: str) -> None:
    if not entity_id or not ha.enabled:
        return
    current = _get_state(entity_id)
    if current == option:
        return
    await ha.call_service_named("input_select", "select_option", {"entity_id": entity_id, "option": option})
    action_log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} SELECT {entity_id} -> {option}")

async def _apply_impianto_live() -> None:
    if cfg.get("runtime", {}).get("mode") != "live":
        return
    if not ha.enabled:
        return
    if not cfg.get("modules_enabled", {}).get("impianto", True):
        return

    ent = cfg.get("entities", {})
    act = cfg.get("actuators", {})

    sel = ent.get("hvac_riscaldamento_select")
    richiesta = ent.get("richiesta_heat_piani")
    clima = ent.get("puffer_consenso_riscaldamento_piani")
    off_centralina = ent.get("off_centralina_termoregolazione")
    r4 = act.get("r4_valve_impianto_da_puffer")

    imp_cfg = cfg.get("impianto", {})
    sel_state = str(_get_state(sel) or imp_cfg.get("source_mode", "AUTO") or "AUTO").strip().upper()
    richiesta_on = _state_is_on(richiesta) if richiesta else bool(imp_cfg.get("richiesta_heat"))

    pdc_ready = _state_is_on(ent.get("source_pdc_ready")) if ent.get("source_pdc_ready") else bool(imp_cfg.get("pdc_ready"))
    volano_ready = _state_is_on(ent.get("source_volano_ready")) if ent.get("source_volano_ready") else bool(imp_cfg.get("volano_ready"))
    caldaia_ready = _state_is_on(ent.get("source_caldaia_ready")) if ent.get("source_caldaia_ready") else bool(imp_cfg.get("caldaia_ready"))
    misc_enable = ent.get("miscelatrice_enable")

    if sel_state not in ("AUTO", "PDC", "VOLANO", "CALDAIA", "PUFFER"):
        sel_state = "AUTO"

    # Se selector AUTO o sorgente non disponibile -> fallback con priorit?
    if sel_state == "AUTO" or (
        (sel_state == "PDC" and not pdc_ready) or
        (sel_state == "VOLANO" and not volano_ready) or
        (sel_state == "CALDAIA" and not caldaia_ready)
    ):
        if pdc_ready:
            source = "PDC"
        elif volano_ready:
            source = "VOLANO"
        elif caldaia_ready:
            source = "CALDAIA"
        else:
            source = "PUFFER"
    else:
        source = sel_state

    r5 = act.get("r5_valve_impianto_da_pdc")
    r31 = act.get("r31_valve_impianto_da_volano")
    r15 = act.get("r15_pump_caldaia_legna")

    if not richiesta_on:
        await _set_actuator(r4, False)
        await _set_actuator(r5, False)
        await _set_actuator(r31, False)
        await _set_actuator(r15, False)
        await _set_climate_hvac_mode(clima, "off")
        await _set_actuator(off_centralina, True)
        if cfg.get("modules_enabled", {}).get("miscelatrice", True):
            await _set_actuator(misc_enable, False)
        return

    # Consenso/centralina
    await _set_actuator(off_centralina, False)

    if source == "PDC":
        await _set_actuator(r5, True)
        await _set_actuator(r31, False)
        await _set_actuator(r4, False)
        await _set_actuator(r15, False)
        await _set_climate_hvac_mode(clima, "off")
    elif source == "VOLANO":
        await _set_actuator(r31, True)
        await _set_actuator(r5, False)
        await _set_actuator(r4, False)
        await _set_actuator(r15, False)
        await _set_climate_hvac_mode(clima, "off")
    elif source == "CALDAIA":
        await _set_actuator(r15, True)
        await _set_actuator(r4, True)
        await _set_actuator(r5, False)
        await _set_actuator(r31, False)
        await _set_climate_hvac_mode(clima, "cool")
    else:  # PUFFER
        await _set_actuator(r4, True)
        await _set_actuator(r5, False)
        await _set_actuator(r31, False)
        await _set_actuator(r15, False)
        await _set_climate_hvac_mode(clima, "cool")

@app.get("/api/status")
async def status():
    return JSONResponse({
        "ha_connected": bool(ha.enabled),
        "token_source": getattr(ha, "token_source", None),
        "version": APP_VERSION,
        "runtime_mode": cfg.get("runtime", {}).get("mode", "dry-run"),
    })

@app.websocket("/ws")
async def ws_endpoint(websocket: WebSocket):
    await websocket.accept()
    ws_clients.add(websocket)
    try:
        while True:
            await websocket.send_json(await _build_snapshot())
            await asyncio.sleep(2)
    except WebSocketDisconnect:
        pass
    finally:
        ws_clients.discard(websocket)

@app.get("/api/actions")
async def actions():
    return JSONResponse({"items": action_log[-50:]})

@app.get("/api/assets")
async def list_assets():
    assets_dir = Path("/app/static/assets")
    if not assets_dir.exists():
        return JSONResponse({"exists": False, "files": []})
    files = sorted([p.name for p in assets_dir.glob("*") if p.is_file()])
    return JSONResponse({"exists": True, "files": files})

@app.get("/api/setpoints")
async def get_setpoints():
    return JSONResponse({
        "acs": cfg.get("acs", {}),
        "puffer": cfg.get("puffer", {}),
        "volano": cfg.get("volano", {}),
        "resistance": cfg.get("resistance", {}),
        "solare": cfg.get("solare", {}),
        "timers": cfg.get("timers", {}),
        "runtime": cfg.get("runtime", {}),
        "modules_enabled": cfg.get("modules_enabled", {}),
        "impianto": cfg.get("impianto", {}),
        "history": cfg.get("history", {}),
        "security": cfg.get("security", {}),
    })

@app.post("/api/setpoints")
async def set_setpoints(payload: dict):
    global cfg
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")
    cfg = apply_setpoints(cfg, payload)
    save_config(cfg)
    return JSONResponse({"ok": True})

@app.get("/api/modules")
async def get_modules():
    return JSONResponse(cfg.get("modules_enabled", {}))

@app.post("/api/modules")
async def set_modules(payload: dict):
    global cfg
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")
    pin_required = cfg.get("security", {}).get("user_pin", "")
    provided = payload.get("pin", "")
    if pin_required and provided != pin_required:
        raise HTTPException(status_code=403, detail="Invalid PIN")
    modules = payload.get("modules", {})
    if not isinstance(modules, dict):
        raise HTTPException(status_code=400, detail="Invalid modules")
    cfg = apply_setpoints(cfg, {"modules_enabled": modules})
    save_config(cfg)
    return JSONResponse({"ok": True})

@app.get("/api/history")
async def history(entity_id: str, hours: int = 24):
    if not ha.enabled:
        raise HTTPException(status_code=400, detail="HA offline")
    hours = max(1, min(int(hours), 48))
    # allow only configured temp sensors with history flag
    ent_cfg = cfg.get("entities", {})
    hist_cfg = cfg.get("history", {})
    allowed = {"t_acs", "t_puffer", "t_volano", "t_solare_mandata"}
    key = None
    for k in allowed:
        if ent_cfg.get(k) == entity_id:
            key = k
            break
    if not key or not hist_cfg.get(key):
        raise HTTPException(status_code=403, detail="History disabled")

    import datetime as dt
    end = dt.datetime.utcnow()
    start = end - dt.timedelta(hours=hours)
    path = f"history/period/{start.isoformat()}"
    params = {
        "filter_entity_id": entity_id,
        "end_time": end.isoformat(),
        "minimal_response": "1",
        "no_attributes": "1"
    }
    data = await ha.api_get(path, params=params)
    return JSONResponse({"items": data or []})

@app.get("/api/entities")
async def get_entities():
    ent = cfg.get("entities", {})
    out = {}
    for k, eid in ent.items():
        if eid:
            st = ha.states.get(eid, {})
            out[k] = {
                "entity_id": eid,
                "state": st.get("state"),
                "attributes": st.get("attributes", {}),
                "icon": entity_icon_map.get(eid)
            }
        else:
            out[k] = {"entity_id": None, "state": None, "attributes": {}, "icon": None}
    return JSONResponse(out)

@app.post("/api/entities")
async def set_entities(payload: dict):
    global cfg
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")
    cfg = apply_entities(cfg, payload)
    save_config(cfg)
    return JSONResponse({"ok": True})

@app.get("/api/actuators")
async def get_actuators():
    act = cfg.get("actuators", {})
    states = {}
    for k, eid in act.items():
        if eid:
            st = ha.states.get(eid, {})
            states[k] = {
                "entity_id": eid,
                "state": st.get("state"),
                "attributes": st.get("attributes", {}),
                "icon": entity_icon_map.get(eid)
            }
        else:
            states[k] = {"entity_id": None, "state": None, "attributes": {}, "icon": None}
    return JSONResponse(states)

@app.post("/api/actuators")
async def set_actuators(payload: dict):
    global cfg
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")
    cfg = apply_actuators(cfg, payload)
    save_config(cfg)
    return JSONResponse({"ok": True})

@app.post("/api/actuate")
async def actuate(payload: dict):
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")
    entity_id = payload.get("entity_id")
    action = payload.get("action")
    manual = bool(payload.get("manual", False))
    if action not in ("on", "off"):
        raise HTTPException(status_code=400, detail="Invalid action")
    if not entity_id or not isinstance(entity_id, str):
        raise HTTPException(status_code=400, detail="Invalid entity_id")
    if not ha.enabled:
        raise HTTPException(status_code=400, detail="HA offline")
    recent_ui_actuations[entity_id] = time.time()
    if manual:
        # R8/R9/R10 restano automatici: non mettere override manuale
        act = cfg.get("actuators", {})
        r8 = act.get("r8_valve_solare_notte_low_temp")
        r9 = act.get("r9_valve_solare_normal_funz")
        r10 = act.get("r10_valve_solare_precedenza_acs")
        if entity_id in (r8, r9, r10):
            manual = False

    if manual:
        # Manuale puro in Admin: non va toccato dalla logica
        if action == "on":
            manual_overrides[entity_id] = True
        else:
            manual_overrides.pop(entity_id, None)
        # Interlock R18/R19: accendine una spegne l'altra
        act = cfg.get("actuators", {})
        r18 = act.get("r18_valve_ritorno_solare_basso")
        r19 = act.get("r19_valve_ritorno_solare_alto")
        if entity_id in (r18, r19) and action == "on":
            other = r19 if entity_id == r18 else r18
            if other:
                manual_overrides.pop(other, None)
                await ha.call_service(other, "off")
    ok = await ha.call_service(entity_id, action)
    return JSONResponse({"ok": bool(ok)})
