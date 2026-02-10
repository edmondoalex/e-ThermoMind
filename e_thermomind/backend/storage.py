import json
from pathlib import Path
from typing import Any, Dict, Iterable

DATA_DIR = Path("/data")
CONF_PATH = DATA_DIR / "thermomind_config.json"

DEFAULT_CONFIG: Dict[str, Any] = {
  "entities": {
    "t_acs": None,
    "t_puffer": None,
    "t_volano": None,
    "t_solare_mandata": None,
    "t_mandata_miscelata": None,
    "t_ritorno_miscelato": None,
    "grid_export_w": None,
    "resistenze_volano_power": None,
    "resistenze_volano_energy": None,
    "hvac_riscaldamento_select": None,
    "richiesta_heat_piani": None,
    "puffer_consenso_riscaldamento_piani": None,
    "off_centralina_termoregolazione": None,
    "source_pdc_ready": None,
    "source_volano_ready": None,
    "source_caldaia_ready": None,
    "miscelatrice_setpoint": None
  },
  "actuators": {
    "r1_valve_comparto_laboratorio": None,
    "r2_valve_comparto_mandata_imp_pt": None,
    "r3_valve_comparto_mandata_imp_m1p": None,
    "r4_valve_impianto_da_puffer": None,
    "r5_valve_impianto_da_pdc": None,
    "r31_valve_impianto_da_volano": None,
    "r6_valve_pdc_to_integrazione_acs": None,
    "r7_valve_pdc_to_integrazione_puffer": None,
    "r8_valve_solare_notte_low_temp": None,
    "r9_valve_solare_normal_funz": None,
    "r10_valve_solare_precedenza_acs": None,
    "r11_pump_mandata_laboratorio": None,
    "r12_pump_mandata_piani": None,
    "r13_pump_pdc_to_acs_puffer": None,
    "r14_pump_puffer_to_acs": None,
    "r15_pump_caldaia_legna": None,
    "r16_cmd_miscelatrice_alza": None,
    "r17_cmd_miscelatrice_abbassa": None,
    "r18_valve_ritorno_solare_basso": None,
    "r19_valve_ritorno_solare_alto": None,
    "r20_ta_caldaia_legna": None,
    "r21_libero": None,
    "r22_resistenza_1_volano_pdc": None,
    "r23_resistenza_2_volano_pdc": None,
    "r24_resistenza_3_volano_pdc": None,
    "generale_resistenze_volano_pdc": None,
    "r25_comparto_generale_pdc": None,
    "r26_comparto_pdc1_avvio": None,
    "r27_comparto_pdc2_avvio": None,
    "r28_scarico_antigelo_mandata_pdc": None,
    "r29_scarico_antigelo_ritorno_pdc": None,
    "r30_alimentazione_caldaia_legna": None
  },
  "acs": {
    "setpoint_c": 55.0,
    "on_delta_c": 2.0,
    "off_hyst_c": 1.0,
    "max_c": 60.0,
    "max_hyst_c": 2.0
  },
  "puffer": {
    "setpoint_c": 55.0,
    "off_hyst_c": 1.0,
    "max_c": 75.0,
    "max_hyst_c": 3.0,
    "min_to_acs_c": 60.0,
    "hyst_to_acs_c": 5.0,
    "delta_to_acs_start_c": 3.0,
    "delta_to_acs_hold_c": 1.5
  },
  "volano": {
    "margin_c": 3.0,
    "max_c": 60.0,
    "max_hyst_c": 2.0,
    "min_to_acs_c": 50.0,
    "hyst_to_acs_c": 5.0,
    "delta_to_acs_start_c": 5.0,
    "delta_to_acs_hold_c": 2.5,
    "delta_to_puffer_start_c": 5.0,
    "delta_to_puffer_hold_c": 2.5
  },
  "miscelatrice": {
    "setpoint_c": 45.0,
    "hyst_c": 0.5,
    "kp": 2.0,
    "min_imp_s": 1.0,
    "max_imp_s": 8.0,
    "pause_s": 5.0,
    "dt_ref_c": 10.0,
    "dt_min_factor": 0.6,
    "dt_max_factor": 1.4,
    "min_temp_c": 20.0,
    "max_temp_c": 80.0,
    "force_impulse_s": 3.0
  },
  "resistance": {
    "enabled": True,
    "off_delay_s": 5,
    "thresholds_w": [1100, 2200, 3300],
    "invert_export_sign": False
  },
  "solare": {
    "mode": "auto",
    "delta_on_c": 5.0,
    "delta_hold_c": 2.5,
    "max_c": 90.0,
    "pv_entity": "",
    "pv_day_w": 1000.0,
    "pv_night_w": 300.0,
    "pv_debounce_s": 300
  },
  "timers": {
    "volano_to_acs_start_s": 5,
    "volano_to_acs_stop_s": 2,
    "volano_to_puffer_start_s": 5,
    "volano_to_puffer_stop_s": 2
  },
  "runtime": {
    "mode": "dry-run",
    "ui_poll_ms": 3000
  },
  "modules_enabled": {
    "resistenze_volano": True,
    "volano_to_acs": False,
    "volano_to_puffer": False,
    "puffer_to_acs": False,
    "solare": False,
    "miscelatrice": False,
    "pdc": False,
    "impianto": False
  },
  "impianto": {
    "source_mode": "AUTO",
    "pdc_ready": False,
    "volano_ready": False,
    "puffer_ready": True,
    "richiesta_heat": False,
    "volano_min_c": 35.0,
    "volano_hyst_c": 2.0,
    "puffer_min_c": 35.0,
    "puffer_hyst_c": 2.0,
    "zones_pt": [],
    "zones_p1": [],
    "zones_mans": [],
    "zones_lab": [],
    "zone_scala": "",
    "cooling_blocked": [],
    "pump_start_delay_s": 9,
    "pump_stop_delay_s": 0,
    "season_mode": "winter"
  },
  "history": {
    "t_acs": False,
    "t_puffer": False,
    "t_volano": False,
    "t_solare_mandata": False,
    "t_mandata_miscelata": False,
    "t_ritorno_miscelato": False,
    "miscelatrice_setpoint": False
  },
  "security": {
    "user_pin": ""
  }
}

_NUM_KEYS = {
  "acs": ["setpoint_c", "on_delta_c", "off_hyst_c", "max_c", "max_hyst_c"],
  "puffer": ["setpoint_c", "off_hyst_c", "max_c", "max_hyst_c", "min_to_acs_c", "hyst_to_acs_c", "delta_to_acs_start_c", "delta_to_acs_hold_c"],
  "miscelatrice": ["setpoint_c", "hyst_c", "kp", "min_imp_s", "max_imp_s", "pause_s", "dt_ref_c", "dt_min_factor", "dt_max_factor", "min_temp_c", "max_temp_c", "force_impulse_s"],
  "solare": ["delta_on_c", "delta_hold_c", "max_c", "pv_day_w", "pv_night_w", "pv_debounce_s"],
  "volano": [
    "margin_c",
    "max_c",
    "max_hyst_c",
    "min_to_acs_c",
    "hyst_to_acs_c",
    "delta_to_acs_start_c",
    "delta_to_acs_hold_c",
    "delta_to_puffer_start_c",
    "delta_to_puffer_hold_c",
  ],
}



def _parse_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(x).strip() for x in value if str(x).strip()]
    if isinstance(value, str):
        return [v.strip() for v in value.split(',') if v.strip()]
    return []
def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except Exception:
        return default

def _float_list_3(value: Any, defaults: Iterable[float]) -> list[float]:
    base = list(defaults)
    if not isinstance(value, (list, tuple)):
        return base[:3]
    out: list[float] = []
    for idx in range(3):
        if idx < len(value):
            out.append(_float(value[idx], base[idx]))
        else:
            out.append(base[idx])
    return out

def normalize_config(raw: Dict[str, Any]) -> Dict[str, Any]:
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if not isinstance(raw, dict):
        return cfg

    ent = raw.get("entities", {})
    if isinstance(ent, dict):
        for key in cfg["entities"].keys():
            val = ent.get(key)
            if val is None:
                cfg["entities"][key] = None
            elif isinstance(val, str):
                cfg["entities"][key] = val.strip() or None

    act = raw.get("actuators", {})
    if isinstance(act, dict):
        for key in cfg["actuators"].keys():
            val = act.get(key)
            if val is None:
                cfg["actuators"][key] = None
            elif isinstance(val, str):
                cfg["actuators"][key] = val.strip() or None

    for section, keys in _NUM_KEYS.items():
        src = raw.get(section, {})
        if isinstance(src, dict):
            for key in keys:
                if key in src:
                    cfg[section][key] = _float(src[key], cfg[section][key])

    res = raw.get("resistance", {})
    if isinstance(res, dict):
        if "enabled" in res:
            cfg["resistance"]["enabled"] = bool(res["enabled"])
        if "off_delay_s" in res:
            cfg["resistance"]["off_delay_s"] = int(_float(res["off_delay_s"], cfg["resistance"]["off_delay_s"]))
        if "invert_export_sign" in res:
            cfg["resistance"]["invert_export_sign"] = bool(res["invert_export_sign"])
        if "thresholds_w" in res:
            cfg["resistance"]["thresholds_w"] = _float_list_3(
                res["thresholds_w"], cfg["resistance"]["thresholds_w"]
            )
    sol = raw.get("solare", {})
    if isinstance(sol, dict):
        if isinstance(sol.get("mode"), str):
            cfg["solare"]["mode"] = sol.get("mode", "auto")
        if isinstance(sol.get("pv_entity"), str):
            cfg["solare"]["pv_entity"] = sol.get("pv_entity", "").strip()
        for key in _NUM_KEYS["solare"]:
            if key in sol:
                cfg["solare"][key] = _float(sol[key], cfg["solare"][key])

    timers = raw.get("timers", {})
    if isinstance(timers, dict):
        # Backward compatibility for older shared timers
        legacy_start = timers.get("valve_to_pump_start_s")
        legacy_stop = timers.get("valve_to_pump_stop_s")
        if legacy_start is not None:
            cfg["timers"]["volano_to_acs_start_s"] = int(_float(legacy_start, cfg["timers"]["volano_to_acs_start_s"]))
            cfg["timers"]["volano_to_puffer_start_s"] = int(_float(legacy_start, cfg["timers"]["volano_to_puffer_start_s"]))
        if legacy_stop is not None:
            cfg["timers"]["volano_to_acs_stop_s"] = int(_float(legacy_stop, cfg["timers"]["volano_to_acs_stop_s"]))
            cfg["timers"]["volano_to_puffer_stop_s"] = int(_float(legacy_stop, cfg["timers"]["volano_to_puffer_stop_s"]))
        if "volano_to_acs_start_s" in timers:
            cfg["timers"]["volano_to_acs_start_s"] = int(_float(timers["volano_to_acs_start_s"], cfg["timers"]["volano_to_acs_start_s"]))
        if "volano_to_acs_stop_s" in timers:
            cfg["timers"]["volano_to_acs_stop_s"] = int(_float(timers["volano_to_acs_stop_s"], cfg["timers"]["volano_to_acs_stop_s"]))
        if "volano_to_puffer_start_s" in timers:
            cfg["timers"]["volano_to_puffer_start_s"] = int(_float(timers["volano_to_puffer_start_s"], cfg["timers"]["volano_to_puffer_start_s"]))
        if "volano_to_puffer_stop_s" in timers:
            cfg["timers"]["volano_to_puffer_stop_s"] = int(_float(timers["volano_to_puffer_stop_s"], cfg["timers"]["volano_to_puffer_stop_s"]))

    runtime = raw.get("runtime", {})
    if isinstance(runtime, dict):
        if isinstance(runtime.get("mode"), str):
            cfg["runtime"]["mode"] = runtime["mode"]
        if "ui_poll_ms" in runtime:
            cfg["runtime"]["ui_poll_ms"] = int(_float(runtime["ui_poll_ms"], cfg["runtime"]["ui_poll_ms"]))

    modules = raw.get("modules_enabled", {})
    if isinstance(modules, dict):
        for key in cfg["modules_enabled"].keys():
            if key in modules:
                cfg["modules_enabled"][key] = bool(modules[key])

    imp = raw.get("impianto", {})
    if isinstance(imp, dict):
        if isinstance(imp.get("source_mode"), str):
            cfg["impianto"]["source_mode"] = imp.get("source_mode", "AUTO").strip().upper()
        for key in ("pdc_ready", "volano_ready", "puffer_ready", "richiesta_heat"):
            if key in imp:
                cfg["impianto"][key] = bool(imp[key])

    hist = raw.get("history", {})
    if isinstance(hist, dict):
        for key in ("t_acs", "t_puffer", "t_volano", "t_solare_mandata", "t_mandata_miscelata", "t_ritorno_miscelato", "miscelatrice_setpoint"):
            if key in hist:
                cfg["history"][key] = bool(hist[key])

    imp = raw.get("impianto", {})
    if isinstance(imp, dict):
        if isinstance(imp.get("source_mode"), str):
            cfg["impianto"]["source_mode"] = imp.get("source_mode", "AUTO").strip().upper()
        for key in ("pdc_ready", "volano_ready", "puffer_ready", "richiesta_heat"):
            if key in imp:
                cfg["impianto"][key] = bool(imp[key])
        for key in ("volano_min_c", "volano_hyst_c", "puffer_min_c", "puffer_hyst_c"):
            if key in imp:
                cfg["impianto"][key] = _float(imp.get(key), cfg["impianto"].get(key, 0.0))
        if "zones_pt" in imp:
            cfg["impianto"]["zones_pt"] = _parse_list(imp.get("zones_pt"))
        if "zones_p1" in imp:
            cfg["impianto"]["zones_p1"] = _parse_list(imp.get("zones_p1"))
        if "zones_mans" in imp:
            cfg["impianto"]["zones_mans"] = _parse_list(imp.get("zones_mans"))
        if "zones_lab" in imp:
            cfg["impianto"]["zones_lab"] = _parse_list(imp.get("zones_lab"))
        if "zone_scala" in imp:
            cfg["impianto"]["zone_scala"] = str(imp.get("zone_scala") or "").strip()
        if "cooling_blocked" in imp:
            cfg["impianto"]["cooling_blocked"] = _parse_list(imp.get("cooling_blocked"))
        if "pump_start_delay_s" in imp:
            cfg["impianto"]["pump_start_delay_s"] = int(_float(imp.get("pump_start_delay_s"), cfg["impianto"]["pump_start_delay_s"]))
        if "pump_stop_delay_s" in imp:
            cfg["impianto"]["pump_stop_delay_s"] = int(_float(imp.get("pump_stop_delay_s"), cfg["impianto"]["pump_stop_delay_s"]))

    security = raw.get("security", {})
    if isinstance(security, dict) and isinstance(security.get("user_pin"), str):
        cfg["security"]["user_pin"] = security.get("user_pin", "")

    return cfg

def apply_setpoints(cfg: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    cfg = normalize_config(cfg)
    if not isinstance(payload, dict):
        return cfg
    for section, keys in _NUM_KEYS.items():
        src = payload.get(section, {})
        if isinstance(src, dict):
            for key in keys:
                if key in src:
                    cfg[section][key] = _float(src[key], cfg[section][key])
    res = payload.get("resistance", {})
    if isinstance(res, dict):
        if "enabled" in res:
            cfg["resistance"]["enabled"] = bool(res["enabled"])
        if "off_delay_s" in res:
            cfg["resistance"]["off_delay_s"] = int(_float(res["off_delay_s"], cfg["resistance"]["off_delay_s"]))
        if "invert_export_sign" in res:
            cfg["resistance"]["invert_export_sign"] = bool(res["invert_export_sign"])
        if "thresholds_w" in res:
            cfg["resistance"]["thresholds_w"] = _float_list_3(
                res["thresholds_w"], cfg["resistance"]["thresholds_w"]
            )
    sol = payload.get("solare", {})
    if isinstance(sol, dict):
        if isinstance(sol.get("mode"), str):
            cfg["solare"]["mode"] = sol.get("mode", "auto")
        if isinstance(sol.get("pv_entity"), str):
            cfg["solare"]["pv_entity"] = sol.get("pv_entity", "").strip()
        for key in _NUM_KEYS["solare"]:
            if key in sol:
                cfg["solare"][key] = _float(sol[key], cfg["solare"][key])
    timers = payload.get("timers", {})
    if isinstance(timers, dict):
        if "volano_to_acs_start_s" in timers:
            cfg["timers"]["volano_to_acs_start_s"] = int(_float(timers["volano_to_acs_start_s"], cfg["timers"]["volano_to_acs_start_s"]))
        if "volano_to_acs_stop_s" in timers:
            cfg["timers"]["volano_to_acs_stop_s"] = int(_float(timers["volano_to_acs_stop_s"], cfg["timers"]["volano_to_acs_stop_s"]))
        if "volano_to_puffer_start_s" in timers:
            cfg["timers"]["volano_to_puffer_start_s"] = int(_float(timers["volano_to_puffer_start_s"], cfg["timers"]["volano_to_puffer_start_s"]))
        if "volano_to_puffer_stop_s" in timers:
            cfg["timers"]["volano_to_puffer_stop_s"] = int(_float(timers["volano_to_puffer_stop_s"], cfg["timers"]["volano_to_puffer_stop_s"]))
    runtime = payload.get("runtime", {})
    if isinstance(runtime, dict):
        if "ui_poll_ms" in runtime:
            cfg["runtime"]["ui_poll_ms"] = int(_float(runtime["ui_poll_ms"], cfg["runtime"]["ui_poll_ms"]))
        if isinstance(runtime.get("mode"), str):
            cfg["runtime"]["mode"] = runtime["mode"]

    modules = payload.get("modules_enabled", {})
    if isinstance(modules, dict):
        for key in cfg["modules_enabled"].keys():
            if key in modules:
                cfg["modules_enabled"][key] = bool(modules[key])

    imp = payload.get("impianto", {})
    if isinstance(imp, dict):
        if isinstance(imp.get("source_mode"), str):
            cfg["impianto"]["source_mode"] = imp.get("source_mode", "AUTO").strip().upper()
        for key in ("pdc_ready", "volano_ready", "puffer_ready", "richiesta_heat"):
            if key in imp:
                cfg["impianto"][key] = bool(imp[key])

    hist = payload.get("history", {})
    if isinstance(hist, dict):
        for key in ("t_acs", "t_puffer", "t_volano", "t_solare_mandata", "t_mandata_miscelata", "t_ritorno_miscelato", "miscelatrice_setpoint"):
            if key in hist:
                cfg["history"][key] = bool(hist[key])

    imp = payload.get("impianto", {})
    if isinstance(imp, dict):
        if isinstance(imp.get("source_mode"), str):
            cfg["impianto"]["source_mode"] = imp.get("source_mode", "AUTO").strip().upper()
        for key in ("pdc_ready", "volano_ready", "puffer_ready", "richiesta_heat"):
            if key in imp:
                cfg["impianto"][key] = bool(imp[key])
        for key in ("volano_min_c", "volano_hyst_c", "puffer_min_c", "puffer_hyst_c"):
            if key in imp:
                cfg["impianto"][key] = _float(imp.get(key), cfg["impianto"].get(key, 0.0))
        if "zones_pt" in imp:
            cfg["impianto"]["zones_pt"] = _parse_list(imp.get("zones_pt"))
        if "zones_p1" in imp:
            cfg["impianto"]["zones_p1"] = _parse_list(imp.get("zones_p1"))
        if "zones_mans" in imp:
            cfg["impianto"]["zones_mans"] = _parse_list(imp.get("zones_mans"))
        if "zones_lab" in imp:
            cfg["impianto"]["zones_lab"] = _parse_list(imp.get("zones_lab"))
        if "zone_scala" in imp:
            cfg["impianto"]["zone_scala"] = str(imp.get("zone_scala") or "").strip()
        if "cooling_blocked" in imp:
            cfg["impianto"]["cooling_blocked"] = _parse_list(imp.get("cooling_blocked"))
        if "pump_start_delay_s" in imp:
            cfg["impianto"]["pump_start_delay_s"] = int(_float(imp.get("pump_start_delay_s"), cfg["impianto"]["pump_start_delay_s"]))
        if "pump_stop_delay_s" in imp:
            cfg["impianto"]["pump_stop_delay_s"] = int(_float(imp.get("pump_stop_delay_s"), cfg["impianto"]["pump_stop_delay_s"]))

    security = payload.get("security", {})
    if isinstance(security, dict) and isinstance(security.get("user_pin"), str):
        cfg["security"]["user_pin"] = security.get("user_pin", "")
    return cfg

def apply_entities(cfg: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    cfg = normalize_config(cfg)
    if not isinstance(payload, dict):
        return cfg
    ent = payload.get("entities", payload)
    if not isinstance(ent, dict):
        return cfg
    for key in cfg["entities"].keys():
        if key in ent:
            val = ent.get(key)
            if val is None:
                cfg["entities"][key] = None
            elif isinstance(val, str):
                cfg["entities"][key] = val.strip() or None
    return cfg

def apply_actuators(cfg: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    cfg = normalize_config(cfg)
    if not isinstance(payload, dict):
        return cfg
    act = payload.get("actuators", payload)
    if not isinstance(act, dict):
        return cfg
    for key in cfg["actuators"].keys():
        if key in act:
            val = act.get(key)
            if val is None:
                cfg["actuators"][key] = None
            elif isinstance(val, str):
                cfg["actuators"][key] = val.strip() or None
            elif isinstance(val, dict):
                ent = val.get("entity_id")
                if ent is None:
                    cfg["actuators"][key] = None
                elif isinstance(ent, str):
                    cfg["actuators"][key] = ent.strip() or None
    return cfg

def load_config() -> Dict[str, Any]:
    if not CONF_PATH.exists():
        return json.loads(json.dumps(DEFAULT_CONFIG))
    try:
        raw = json.loads(CONF_PATH.read_text(encoding="utf-8"))
        return normalize_config(raw)
    except Exception:
        return json.loads(json.dumps(DEFAULT_CONFIG))

def save_config(cfg: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    CONF_PATH.write_text(json.dumps(normalize_config(cfg), indent=2, ensure_ascii=False), encoding="utf-8")
