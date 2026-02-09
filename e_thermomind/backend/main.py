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
    return JSONResponse(data)

def _get_state(entity_id: str | None) -> str | None:
    if not entity_id:
        return None
    return ha.states.get(entity_id, {}).get("state")

async def _build_snapshot() -> dict:
    data = compute_decision(cfg, ha.states)
    await _apply_resistance_live(data)
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
        "actions": action_log[-20:],
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
    key = _actuator_key_for_entity(entity_id)
    if not key:
        return
    module_key = _module_for_actuator_key(key)
    if module_key and not cfg.get("modules_enabled", {}).get(module_key, True):
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
    current = _get_state(entity_id)
    if want_on and current != "on":
        await ha.call_service(entity_id, "on")
        action_log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} ON {entity_id}")
    if (not want_on) and current != "off":
        await ha.call_service(entity_id, "off")
        action_log.append(f"{time.strftime('%Y-%m-%d %H:%M:%S')} OFF {entity_id}")

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
        current_r22 = _get_state(r22) == "on" if r22 else False
        current_r23 = _get_state(r23) == "on" if r23 else False
        current_r24 = _get_state(r24) == "on" if r24 else False
        want_general = bool(desired["r22"] or desired["r23"] or desired["r24"] or current_r22 or current_r23 or current_r24)
        await _set_resistance(rg, want_general)

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
    return JSONResponse({"items": action_log[-20:]})

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
        "runtime": cfg.get("runtime", {}),
        "modules_enabled": cfg.get("modules_enabled", {}),
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
    if action not in ("on", "off"):
        raise HTTPException(status_code=400, detail="Invalid action")
    if not entity_id or not isinstance(entity_id, str):
        raise HTTPException(status_code=400, detail="Invalid entity_id")
    if not ha.enabled:
        raise HTTPException(status_code=400, detail="HA offline")
    recent_ui_actuations[entity_id] = time.time()
    ok = await ha.call_service(entity_id, action)
    return JSONResponse({"ok": bool(ok)})
