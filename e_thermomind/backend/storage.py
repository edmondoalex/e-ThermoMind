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
    "grid_export_w": None
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
    "max_hyst_c": 3.0
  },
  "volano": {
    "margin_c": 3.0,
    "max_c": 60.0,
    "max_hyst_c": 2.0,
    "delta_to_acs_start_c": 5.0,
    "delta_to_acs_hold_c": 2.5,
    "delta_to_puffer_start_c": 5.0,
    "delta_to_puffer_hold_c": 2.5
  },
  "resistance": {
    "enabled": True,
    "off_delay_s": 5,
    "thresholds_w": [1100, 2200, 3300],
    "invert_export_sign": False
  },
  "runtime": {
    "mode": "dry-run",
    "ui_poll_ms": 3000
  }
}

_NUM_KEYS = {
  "acs": ["setpoint_c", "on_delta_c", "off_hyst_c", "max_c", "max_hyst_c"],
  "puffer": ["setpoint_c", "off_hyst_c", "max_c", "max_hyst_c"],
  "volano": [
    "margin_c",
    "max_c",
    "max_hyst_c",
    "delta_to_acs_start_c",
    "delta_to_acs_hold_c",
    "delta_to_puffer_start_c",
    "delta_to_puffer_hold_c",
  ],
}

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

    runtime = raw.get("runtime", {})
    if isinstance(runtime, dict):
        if isinstance(runtime.get("mode"), str):
            cfg["runtime"]["mode"] = runtime["mode"]
        if "ui_poll_ms" in runtime:
            cfg["runtime"]["ui_poll_ms"] = int(_float(runtime["ui_poll_ms"], cfg["runtime"]["ui_poll_ms"]))

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
    runtime = payload.get("runtime", {})
    if isinstance(runtime, dict) and "ui_poll_ms" in runtime:
        cfg["runtime"]["ui_poll_ms"] = int(_float(runtime["ui_poll_ms"], cfg["runtime"]["ui_poll_ms"]))
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
