from typing import Any, Dict

def _f(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default

def _thr_list(value: Any) -> list[float]:
    base = [1100.0, 2200.0, 3300.0]
    if not isinstance(value, (list, tuple)):
        return base
    out: list[float] = []
    for idx in range(3):
        if idx < len(value):
            out.append(_f(value[idx], base[idx]))
        else:
            out.append(base[idx])
    return out

_LAST: Dict[str, Any] = {
    "dest": None,
    "source_to_acs": None,
    "volano_to_puffer": False
}

def compute_decision(cfg: Dict[str, Any], ha_states: Dict[str, Any], now: float | None = None) -> Dict[str, Any]:
    ent = cfg.get("entities", {})
    acs_cfg = cfg.get("acs", {})
    puf_cfg = cfg.get("puffer", {})
    vol_cfg = cfg.get("volano", {})
    res_cfg = cfg.get("resistance", {})

    def get_num(eid: str | None, default: float = 0.0) -> float:
        if not eid:
            return default
        st = ha_states.get(eid, {}).get("state")
        return _f(st, default)

    t_acs = get_num(ent.get("t_acs"), 0.0)
    t_puffer = get_num(ent.get("t_puffer"), 0.0)
    t_volano = get_num(ent.get("t_volano"), 0.0)
    t_sol = get_num(ent.get("t_solare_mandata"), 0.0)
    export_w = get_num(ent.get("grid_export_w"), 0.0)

    if res_cfg.get("invert_export_sign"):
        export_w = -export_w

    acs_sp = float(acs_cfg.get("setpoint_c", 55.0))
    acs_off_h = float(acs_cfg.get("off_hyst_c", 1.0))
    acs_on_delta = float(acs_cfg.get("on_delta_c", 2.0))
    acs_off_delta = float(acs_cfg.get("off_hyst_c", 1.0))
    acs_ok = t_acs >= (acs_sp + acs_off_delta)
    acs_need = t_acs <= (acs_sp - acs_on_delta)

    acs_max = float(acs_cfg.get("max_c", 60.0))
    vol_max = float(vol_cfg.get("max_c", 60.0))
    puf_max = float(puf_cfg.get("max_c", 75.0))

    acs_max_hit = t_acs >= acs_max
    vol_max_hit = t_volano >= vol_max
    puf_max_hit = t_puffer >= puf_max

    puf_sp = float(puf_cfg.get("setpoint_c", 55.0))
    puf_off_h = float(puf_cfg.get("off_hyst_c", 1.0))
    puf_need = (t_puffer <= (puf_sp - puf_off_h)) and (not puf_max_hit)

    if acs_max_hit:
        dest = "OFF"
        dest_reason = f"ACS_MAX: {t_acs:.1f}°C >= {acs_max:.1f}°C"
    elif acs_need:
        dest = "ACS"
        dest_reason = f"ACS sotto target: {t_acs:.1f}°C <= {acs_sp - acs_on_delta:.1f}°C"
    elif puf_need:
        dest = "PUFFER"
        dest_reason = f"ACS ok; puffer sotto target: {t_puffer:.1f}°C < {puf_sp - puf_off_h:.1f}°C"
    else:
        dest = "OFF"
        dest_reason = "Nessuna destinazione utile."

    solar_cfg = cfg.get("solare", {})
    solar_delta_on = float(solar_cfg.get("delta_on_c", 5.0))
    solar_delta_hold = float(solar_cfg.get("delta_hold_c", 2.5))
    last_source = _LAST.get("source_to_acs")
    delta_start = float(vol_cfg.get("delta_to_acs_start_c", 5.0))
    delta_hold = float(vol_cfg.get("delta_to_acs_hold_c", 2.5))
    puf_delta_start = float(vol_cfg.get("delta_to_puffer_start_c", 5.0))
    puf_delta_hold = float(vol_cfg.get("delta_to_puffer_hold_c", 2.5))
    puf_to_acs_start = float(puf_cfg.get("delta_to_acs_start_c", 3.0))
    puf_to_acs_hold = float(puf_cfg.get("delta_to_acs_hold_c", 1.5))
    last_vol_to_puf = bool(_LAST.get("volano_to_puffer"))

    if dest == "ACS" and (t_sol >= t_acs + solar_delta_on) and (not acs_max_hit):
        source_to_acs = "SOLAR"
        source_reason = f"T_SOL {t_sol:.1f}?C >= T_ACS+delta {t_acs + solar_delta_on:.1f}?C"
    elif dest == "ACS" and last_source == "SOLAR" and (t_sol >= t_acs + solar_delta_hold) and (not acs_max_hit):
        source_to_acs = "SOLAR"
        source_reason = f"T_SOL {t_sol:.1f}?C >= T_ACS+delta_hold {t_acs + solar_delta_hold:.1f}?C"
    elif dest == "ACS" and (t_volano >= t_acs + delta_start) and (not vol_max_hit):
        source_to_acs = "VOLANO"
        source_reason = f"T_VOL {t_volano:.1f}?C >= T_ACS+{delta_start:.1f}?C ({t_acs + delta_start:.1f}?C)"
    elif dest == "ACS" and last_source == "VOLANO" and (t_volano >= t_acs + delta_hold) and (not vol_max_hit):
        source_to_acs = "VOLANO"
        source_reason = f"T_VOL {t_volano:.1f}?C >= T_ACS+{delta_hold:.1f}?C ({t_acs + delta_hold:.1f}?C)"
    elif dest == "ACS" and (t_puffer >= t_acs + puf_to_acs_start):
        source_to_acs = "PUFFER"
        source_reason = f"T_PUF {t_puffer:.1f}?C >= T_ACS+delta {t_acs + puf_to_acs_start:.1f}?C"
    elif dest == "ACS" and last_source == "PUFFER" and (t_puffer >= t_acs + puf_to_acs_hold):
        source_to_acs = "PUFFER"
        source_reason = f"T_PUF {t_puffer:.1f}?C >= T_ACS+delta_hold {t_acs + puf_to_acs_hold:.1f}?C"
    else:
        source_to_acs = "OFF"
        source_reason = "Nessuna sorgente selezionata (v0.1)."

    volano_to_puffer = False
    if dest == "PUFFER" and (not vol_max_hit):
        if t_volano >= t_puffer + puf_delta_start:
            volano_to_puffer = True
        elif last_vol_to_puf and (t_volano >= t_puffer + puf_delta_hold):
            volano_to_puffer = True

    step = 0
    if dest in ("ACS", "PUFFER") and (not vol_max_hit) and res_cfg.get("enabled", True):
        thr = _thr_list(res_cfg.get("thresholds_w", [1100, 2200, 3300]))
        if export_w >= thr[2]:
            step = 3
        elif export_w >= thr[1]:
            step = 2
        elif export_w >= thr[0]:
            step = 1

    charge_buffer = "RESISTANCE" if step > 0 else "OFF"
    if vol_max_hit:
        charge_reason = f"VOLANO_MAX: {t_volano:.1f}°C >= {vol_max:.1f}°C"
    elif dest == "OFF":
        charge_reason = dest_reason
    else:
        charge_reason = (
            f"Export {export_w:.0f}W -> step {step}/3 (OFF delay {res_cfg.get('off_delay_s',5)}s in v0.2)."
        )

    _LAST["dest"] = dest
    _LAST["source_to_acs"] = source_to_acs
    _LAST["volano_to_puffer"] = volano_to_puffer

    return {
        "inputs": {
            "t_acs": t_acs,
            "t_puffer": t_puffer,
            "t_volano": t_volano,
            "t_solare_mandata": t_sol,
            "grid_export_w": export_w
        },
        "computed": {
            "acs_sp": acs_sp,
            "acs_ok": acs_ok,
            "acs_need": acs_need,
            "dest": dest,
            "dest_reason": dest_reason,
            "source_to_acs": source_to_acs,
            "source_reason": source_reason,
            "charge_buffer": charge_buffer,
            "charge_reason": charge_reason,
            "resistance_step": step,
            "flags": {
                "volano_to_acs": source_to_acs == "VOLANO",
                "puffer_to_acs": source_to_acs == "PUFFER",
                "solare_to_acs": source_to_acs == "SOLAR",
                "volano_to_puffer": volano_to_puffer
            },
            "module_reasons": {
                "solare": source_reason if source_to_acs == "SOLAR" else "Solare non attivo per ACS.",
                "volano_to_acs": source_reason if source_to_acs == "VOLANO" else "Volano → ACS non attivo.",
                "puffer_to_acs": source_reason if source_to_acs == "PUFFER" else "Puffer → ACS non attivo.",
                "volano_to_puffer": (
                    f"T_VOL {t_volano:.1f}?C >= T_PUF+{puf_delta_start:.1f}?C ({t_puffer + puf_delta_start:.1f}?C)"
                    if volano_to_puffer
                    else f"T_VOL {t_volano:.1f}?C < T_PUF+{puf_delta_hold:.1f}?C ({t_puffer + puf_delta_hold:.1f}?C)"
                ),
                "resistenze_volano": charge_reason
            },
            "state": {
                "last_dest": _LAST.get("dest"),
                "last_source_to_acs": _LAST.get("source_to_acs")
            },
            "safety": {
                "acs_max_hit": acs_max_hit,
                "volano_max_hit": vol_max_hit,
                "puffer_max_hit": puf_max_hit
            }
        }
    }
