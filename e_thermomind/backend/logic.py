from typing import Any, Dict
import time

def _f(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default



def _is_on_state(state: Any) -> bool:
    if state is None:
        return False
    sval = str(state).strip().lower()
    return sval in ("on", "true", "1", "yes", "heat", "heating")
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

def _parse_hour_float(value: Any, default: float) -> float:
    try:
        v = float(value)
        if v < 0:
            return 0.0
        if v > 23.99:
            return 23.99
        return v
    except Exception:
        pass
    try:
        s = str(value).strip()
        if ":" in s:
            hh, mm = s.split(":", 1)
            h = int(hh)
            m = int(mm)
            if h < 0 or h > 23 or m < 0 or m > 59:
                return default
            return h + (m / 60.0)
    except Exception:
        pass
    return default

_LAST: Dict[str, Any] = {
    "dest": None,
    "source_to_acs": None,
    "impianto_source": None,
    "volano_to_puffer": False,
    "gas_vol_ok": False,
    "gas_puf_ok": False,
    "res_step": 0,
    "res_step_ts": 0.0,
    "res_base": None,
    "heater_easas": False,
    "heater_privato": False
}

def _zone_active(state: Any, hvac_action: Any, cooling_blocked: bool) -> bool:
    if cooling_blocked:
        return False
    sval = str(state or "").strip().lower()
    action = str(hvac_action or "").strip().lower()
    if sval in ("off", "idle", "unavailable", "unknown"):
        return False
    return action in ("heating", "cooling")

def compute_decision(cfg: Dict[str, Any], ha_states: Dict[str, Any], now: float | None = None) -> Dict[str, Any]:
    now_ts = time.time() if now is None else float(now)
    ent = cfg.get("entities", {})
    acs_cfg = cfg.get("acs", {})
    puf_cfg = cfg.get("puffer", {})
    vol_cfg = cfg.get("volano", {})
    res_cfg = cfg.get("resistance", {})
    curve_cfg = cfg.get("curva_climatica", {})
    modules_enabled = cfg.get("modules_enabled", {})
    resistenze_enabled = modules_enabled.get("resistenze_volano", True)
    solare_enabled = modules_enabled.get("solare", True)
    volano_to_acs_enabled = modules_enabled.get("volano_to_acs", True)
    volano_to_puffer_enabled = modules_enabled.get("volano_to_puffer", True)
    puffer_to_acs_enabled = modules_enabled.get("puffer_to_acs", True)
    impianto_enabled = modules_enabled.get("impianto", True)
    pdc_enabled = modules_enabled.get("pdc", True)
    miscelatrice_enabled = modules_enabled.get("miscelatrice", True)
    curve_enabled = modules_enabled.get("curva_climatica", True)
    gas_cfg = cfg.get("gas_emergenza", {})
    gas_enabled = modules_enabled.get("gas_emergenza", False)
    legna_cfg = cfg.get("caldaia_legna", {})
    legna_enabled = modules_enabled.get("caldaia_legna", False)

    def get_num(eid: str | None, default: float = 0.0) -> float:
        if not eid:
            return default
        st = ha_states.get(eid, {}).get("state")
        return _f(st, default)
    def get_text(eid: str | None, default: str = "") -> str:
        if not eid:
            return default
        st = ha_states.get(eid, {}).get("state")
        return default if st is None else str(st)
    def get_num_optional(eid: str | None):
        if not eid:
            return None
        st = ha_states.get(eid, {}).get("state")
        return _f(st, None)

    t_acs = get_num_optional(ent.get("t_acs"))
    if t_acs is None:
        t_acs = get_num(ent.get("t_acs_alto"), 0.0)
    t_acs_alto = get_num(ent.get("t_acs_alto"), 0.0)
    t_acs_medio = get_num(ent.get("t_acs_medio"), 0.0)
    t_acs_basso = get_num(ent.get("t_acs_basso"), 0.0)
    t_puffer = get_num_optional(ent.get("t_puffer"))
    if t_puffer is None:
        t_puffer = get_num(ent.get("t_puffer_alto"), 0.0)
    t_puffer_alto = get_num(ent.get("t_puffer_alto"), 0.0)
    t_puffer_medio = get_num(ent.get("t_puffer_medio"), 0.0)
    t_puffer_basso = get_num(ent.get("t_puffer_basso"), 0.0)
    t_volano = get_num_optional(ent.get("t_volano"))
    if t_volano is None:
        t_volano = get_num(ent.get("t_volano_alto"), 0.0)
    t_volano_alto = get_num(ent.get("t_volano_alto"), 0.0)
    t_volano_basso = get_num(ent.get("t_volano_basso"), 0.0)
    t_sol = get_num(ent.get("t_solare_mandata"), 0.0)
    col_status_code = get_text(ent.get("collettore_status_code"), "")
    col_status = get_text(ent.get("collettore_status"), "")
    col_datetime = get_text(ent.get("collettore_datetime"), "")
    col_energy_day = get_num(ent.get("collettore_energy_day_kwh"), 0.0)
    col_energy_total = get_num(ent.get("collettore_energy_total_kwh"), 0.0)
    col_flow = get_num(ent.get("collettore_flow_lmin"), 0.0)
    sol_flow = get_num_optional(ent.get("solare_flow_lmin"))
    if sol_flow is None:
        sol_flow = col_flow
    col_pwm = get_num(ent.get("collettore_pwm_pct"), 0.0)
    col_status2 = get_text(ent.get("collettore_status2"), "")
    col_t_ext = get_num(ent.get("collettore_temp_esterna"), None)
    col_tsa1 = get_num(ent.get("collettore_tsa1"), 0.0)
    col_tse = get_num(ent.get("collettore_tse"), 0.0)
    col_tsv = get_num(ent.get("collettore_tsv"), 0.0)
    col_twu = get_num(ent.get("collettore_twu"), 0.0)
    t_esterna = get_num(ent.get("t_esterna"), None)
    t_mandata_mix = get_num(ent.get("t_mandata_miscelata"), 0.0)
    t_ritorno_mix = get_num(ent.get("t_ritorno_miscelato"), 0.0)
    export_w = get_num(ent.get("grid_export_w"), 0.0)
    extra_safe_w = get_num(ent.get("extra_safe_w"), 0.0)
    if extra_safe_w < 0:
        extra_safe_w = 0.0
    extra_safe_total_w = get_num(ent.get("extra_safe_total_w"), 0.0)
    if extra_safe_total_w < 0:
        extra_safe_total_w = 0.0
    battery_output_w = get_num(ent.get("battery_output_w"), 0.0)
    pv_power_w = get_num(ent.get("pv_power_w"), 0.0)
    if pv_power_w < 0:
        pv_power_w = 0.0
    battery_temp_c = get_num(ent.get("battery_temp_c"), None)
    battery_soc = get_num_optional(ent.get("battery_soc"))
    battery_temp_c_easas = get_num_optional(ent.get("battery_temp_c_easas"))
    battery_temp_c_privato = get_num_optional(ent.get("battery_temp_c_privato"))
    battery_soc_easas = get_num_optional(ent.get("battery_soc_easas"))
    battery_soc_privato = get_num_optional(ent.get("battery_soc_privato"))
    export_w_easas = get_num_optional(ent.get("grid_export_w_easas"))
    export_w_privato = get_num_optional(ent.get("grid_export_w_privato"))
    batt_out_easas = get_num_optional(ent.get("battery_output_w_easas"))
    batt_out_privato = get_num_optional(ent.get("battery_output_w_privato"))
    pv_power_easas = get_num_optional(ent.get("pv_power_w_easas"))
    pv_power_privato = get_num_optional(ent.get("pv_power_w_privato"))
    res_power_w = get_num(ent.get("resistenze_volano_power"), 0.0)
    if res_power_w < 0:
        res_power_w = 0.0
    t_mandata_legna = get_num(ent.get("t_mandata_caldaia_legna"), None)
    t_ritorno_legna = get_num(ent.get("t_ritorno_caldaia_legna"), None)
    t_caldaia_legna = get_num(ent.get("t_caldaia_legna"), None)

    if res_cfg.get("invert_export_sign"):
        export_w = -export_w
    if export_w_easas is not None:
        export_w = export_w_easas
    if batt_out_easas is not None:
        battery_output_w = batt_out_easas
    if pv_power_easas is not None:
        pv_power_w = pv_power_easas
    if battery_temp_c_easas is not None:
        battery_temp_c = battery_temp_c_easas
    if battery_soc_easas is not None:
        battery_soc = battery_soc_easas

    def _interp_curve(temp_c: float, points: list[dict], mode: str) -> float:
        if not points:
            return 0.0
        pts = sorted([p for p in points if isinstance(p, dict) and "t" in p and "w" in p], key=lambda x: float(x["t"]))
        if not pts:
            return 0.0
        if temp_c <= float(pts[0]["t"]):
            return float(pts[0]["w"])
        if temp_c >= float(pts[-1]["t"]):
            return float(pts[-1]["w"])
        for i in range(1, len(pts)):
            t0 = float(pts[i - 1]["t"])
            t1 = float(pts[i]["t"])
            if temp_c <= t1:
                w0 = float(pts[i - 1]["w"])
                w1 = float(pts[i]["w"])
                if mode == "step":
                    return w0
                if t1 == t0:
                    return w1
                ratio = (temp_c - t0) / (t1 - t0)
                return w0 + (w1 - w0) * ratio
        return float(pts[-1]["w"])

    def _calc_profile(name: str, temp_c: float | None, soc_pct: float | None, export_val: float | None, batt_out: float | None, curve_cfg: dict) -> dict:
        calc_on = bool(curve_cfg.get("calc_extra_safe", False))
        interp_mode = str(curve_cfg.get("interp", "linear")).lower()
        curve = curve_cfg.get("charge_curve", [])
        soc_curve = curve_cfg.get("soc_curve", [])
        export_val = 0.0 if export_val is None else float(export_val)
        batt_out = 0.0 if batt_out is None else float(batt_out)
        if not calc_on or temp_c is None:
            return {"extra_safe_w": 0.0, "extra_safe_total_w": 0.0, "max_charge_w": 0.0, "headroom_w": 0.0,
                    "temp_c": temp_c, "soc_pct": soc_pct, "export_w": export_val, "battery_output_w": batt_out}
        max_charge_w = _interp_curve(float(temp_c), curve, interp_mode)
        if soc_pct is not None and soc_curve:
            try:
                pts = sorted([p for p in soc_curve if isinstance(p, dict) and "soc" in p and "w" in p],
                             key=lambda x: float(x["soc"]))
                if pts:
                    # step: take last point with soc <= current
                    limit_w = None
                    for p in pts:
                        if soc_pct >= float(p["soc"]):
                            limit_w = float(p["w"])
                    if limit_w is not None:
                        max_charge_w = min(max_charge_w, limit_w)
            except Exception:
                pass
        current_charge_w = max(0.0, -batt_out)
        headroom_w = max(0.0, max_charge_w - current_charge_w)
        calc_extra_safe_w = max(0.0, export_val - headroom_w)
        calc_extra_total_w = max(0.0, export_val)
        return {
            "extra_safe_w": calc_extra_safe_w,
            "extra_safe_total_w": calc_extra_total_w,
            "max_charge_w": max_charge_w,
            "headroom_w": headroom_w,
            "temp_c": temp_c,
            "soc_pct": soc_pct,
            "export_w": export_val,
            "battery_output_w": batt_out
        }

    profiles_cfg = cfg.get("energy_profiles", {})
    easas_cfg = profiles_cfg.get("easas", cfg.get("energy", {})) if isinstance(profiles_cfg, dict) else cfg.get("energy", {})
    priv_cfg = profiles_cfg.get("privato", cfg.get("energy", {})) if isinstance(profiles_cfg, dict) else cfg.get("energy", {})

    easas = _calc_profile(
        "easas",
        battery_temp_c_easas if battery_temp_c_easas is not None else battery_temp_c,
        battery_soc_easas if battery_soc_easas is not None else battery_soc,
        export_w_easas if export_w_easas is not None else export_w,
        batt_out_easas if batt_out_easas is not None else battery_output_w,
        easas_cfg if isinstance(easas_cfg, dict) else {}
    )
    privato = _calc_profile(
        "privato",
        battery_temp_c_privato,
        battery_soc_privato,
        export_w_privato,
        batt_out_privato,
        priv_cfg if isinstance(priv_cfg, dict) else {}
    )

    def _calc_heater(profile_key: str, temp_c: float | None, pv_w: float | None, cfg_heater: dict, last_on: bool) -> dict:
        enabled = bool(cfg_heater.get("enabled", True))
        comfort_c = float(cfg_heater.get("comfort_c", 22.0))
        hyst_c = float(cfg_heater.get("hyst_c", 1.0))
        pv_on_w = float(cfg_heater.get("pv_on_w", 300.0))
        pv_w = 0.0 if pv_w is None else float(pv_w)
        on = False
        reason = ""
        if not enabled:
            on = False
            reason = "Disabilitato"
        elif temp_c is None:
            on = False
            reason = "Temp batt n/d"
        elif pv_w < pv_on_w:
            on = False
            reason = f"FV {pv_w:.0f}W < soglia {pv_on_w:.0f}W"
        else:
            if last_on:
                on = temp_c < comfort_c
            else:
                on = temp_c <= (comfort_c - hyst_c)
            reason = f"T={temp_c:.1f}C | comfort {comfort_c:.1f}C | hyst {hyst_c:.1f}C | FV {pv_w:.0f}W"
        return {"on": on, "temp_c": temp_c, "pv_w": pv_w, "comfort_c": comfort_c, "hyst_c": hyst_c, "pv_on_w": pv_on_w, "reason": reason}

    heater_cfg = cfg.get("energy_heater", {})
    easas_heater = _calc_heater(
        "easas",
        battery_temp_c_easas if battery_temp_c_easas is not None else battery_temp_c,
        pv_power_easas if pv_power_easas is not None else pv_power_w,
        heater_cfg.get("easas", {}) if isinstance(heater_cfg, dict) else {},
        bool(_LAST.get("heater_easas", False))
    )
    privato_heater = _calc_heater(
        "privato",
        battery_temp_c_privato,
        pv_power_privato,
        heater_cfg.get("privato", {}) if isinstance(heater_cfg, dict) else {},
        bool(_LAST.get("heater_privato", False))
    )

    extra_safe_w = easas["extra_safe_w"]
    extra_safe_total_w = easas["extra_safe_total_w"]

    available_w = export_w
    if extra_safe_total_w > available_w:
        available_w = extra_safe_total_w
    if available_w < 0:
        available_w = 0.0

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
    flow_min_lmin = float(solar_cfg.get("flow_min_lmin", 0.0))
    solar_flow_ok = sol_flow >= flow_min_lmin
    misc_cfg = cfg.get("miscelatrice", {})
    solar_delta_on = float(solar_cfg.get("delta_on_c", 5.0))
    solar_delta_hold = float(solar_cfg.get("delta_hold_c", 2.5))
    last_source = _LAST.get("source_to_acs")
    delta_start = float(vol_cfg.get("delta_to_acs_start_c", 5.0))
    delta_hold = float(vol_cfg.get("delta_to_acs_hold_c", 2.5))
    puf_delta_start = float(vol_cfg.get("delta_to_puffer_start_c", 5.0))
    puf_delta_hold = float(vol_cfg.get("delta_to_puffer_hold_c", 2.5))
    vol_min_puf = float(vol_cfg.get("min_to_puffer_c", 55.0))
    vol_h_puf = float(vol_cfg.get("hyst_to_puffer_c", 2.0))
    puf_to_acs_start = float(puf_cfg.get("delta_to_acs_start_c", 3.0))
    puf_to_acs_hold = float(puf_cfg.get("delta_to_acs_hold_c", 1.5))
    vol_min_acs = float(vol_cfg.get("min_to_acs_c", 50.0))
    vol_h_acs = float(vol_cfg.get("hyst_to_acs_c", 5.0))
    puf_min_acs = float(puf_cfg.get("min_to_acs_c", 60.0))
    puf_h_acs = float(puf_cfg.get("hyst_to_acs_c", 5.0))
    last_vol_to_puf = bool(_LAST.get("volano_to_puffer"))
    if solare_enabled and solar_flow_ok and (t_sol >= t_acs + solar_delta_on) and (t_acs < acs_sp) and (not acs_max_hit):
        source_to_acs = "SOLAR"
        source_reason = f"T_SOL {t_sol:.1f}°C >= T_ACS+delta {t_acs + solar_delta_on:.1f}°C"
    elif solare_enabled and solar_flow_ok and last_source == "SOLAR" and (t_sol >= t_acs + solar_delta_hold) and (t_acs < acs_sp) and (not acs_max_hit):
        source_to_acs = "SOLAR"
        source_reason = f"T_SOL {t_sol:.1f}°C >= T_ACS+delta_hold {t_acs + solar_delta_hold:.1f}°C"
    elif volano_to_acs_enabled and dest == "ACS" and (t_volano >= t_acs + delta_start) and (t_volano >= vol_min_acs + vol_h_acs):
        source_to_acs = "VOLANO"
        source_reason = f"T_VOL {t_volano:.1f}°C >= T_ACS+{delta_start:.1f}°C ({t_acs + delta_start:.1f}°C)"
    elif volano_to_acs_enabled and dest == "ACS" and last_source == "VOLANO" and (t_volano >= t_acs + delta_hold) and (t_volano >= vol_min_acs):
        source_to_acs = "VOLANO"
        source_reason = f"T_VOL {t_volano:.1f}°C >= T_ACS+{delta_hold:.1f}°C ({t_acs + delta_hold:.1f}°C)"
    elif puffer_to_acs_enabled and dest == "ACS" and (t_puffer >= t_acs + puf_to_acs_start) and (t_puffer >= puf_min_acs + puf_h_acs):
        source_to_acs = "PUFFER"
        source_reason = f"T_PUF {t_puffer:.1f}°C >= T_ACS+delta {t_acs + puf_to_acs_start:.1f}°C"
    elif puffer_to_acs_enabled and dest == "ACS" and last_source == "PUFFER" and (t_puffer >= t_acs + puf_to_acs_hold) and (t_puffer >= puf_min_acs):
        source_to_acs = "PUFFER"
        source_reason = f"T_PUF {t_puffer:.1f}°C >= T_ACS+delta_hold {t_acs + puf_to_acs_hold:.1f}°C"
    else:
        source_to_acs = "OFF"
        disabled = []
        if not solare_enabled:
            disabled.append("SOLARE")
        if not volano_to_acs_enabled:
            disabled.append("VOLANO->ACS")
        if not puffer_to_acs_enabled:
            disabled.append("PUFFER->ACS")
        disabled_txt = f" Moduli OFF: {', '.join(disabled)}." if disabled else ""
        source_reason = f"Nessuna sorgente selezionata (v0.1).{disabled_txt}"

    runtime_cfg = cfg.get("runtime", {})
    force_until = float(runtime_cfg.get("force_acs_puffer_until_ts", 0.0) or 0.0)
    force_active = force_until > now_ts
    force_remaining_s = max(0, int(force_until - now_ts)) if force_active else 0
    force_can_apply = bool(puffer_to_acs_enabled and dest == "ACS" and (not acs_max_hit) and (t_puffer > t_acs))
    force_reason = "Forzatura OFF."
    if force_active:
        if force_can_apply:
            source_to_acs = "PUFFER"
            source_reason = "Forzatura emergenza ACS da PUFFER attiva."
            force_reason = (
                f"Forzatura ACS da PUFFER attiva ({force_remaining_s}s). "
                f"T_PUF {t_puffer:.1f}C > T_ACS {t_acs:.1f}C"
            )
        else:
            force_reason = (
                f"Forzatura attiva ma non applicabile ({force_remaining_s}s): "
                f"Dest={dest} | ACS_MAX={'SI' if acs_max_hit else 'NO'} | "
                f"T_PUF {t_puffer:.1f}C | T_ACS {t_acs:.1f}C"
            )

    force_vtp_until = float(runtime_cfg.get("force_volano_puffer_until_ts", 0.0) or 0.0)
    force_vtp_active = force_vtp_until > now_ts
    force_vtp_remaining_s = max(0, int(force_vtp_until - now_ts)) if force_vtp_active else 0
    force_vtp_can_apply = bool(
        volano_to_puffer_enabled
        and (not puf_max_hit)
        and (t_volano >= t_puffer + puf_delta_hold)
        and (t_volano >= vol_min_puf)
    )
    force_vtp_reason = "Forzatura OFF."
    if not force_vtp_active and not force_vtp_can_apply:
        force_vtp_reason = (
            f"Forzatura OFF: non applicabile. "
            f"Modulo={'ON' if volano_to_puffer_enabled else 'OFF'} | Dest={dest} | Source={source_to_acs} | "
            f"PUF_MAX={'SI' if puf_max_hit else 'NO'} | T_VOL {t_volano:.1f}C | T_PUF {t_puffer:.1f}C | "
            f"serve T_VOL >= T_PUF+{puf_delta_hold:.1f}C ({t_puffer + puf_delta_hold:.1f}C)"
        )

    volano_to_puffer = False
    evening_dump_active = False
    evening_dump_reason = ""
    if volano_to_puffer_enabled and dest == "PUFFER" and (not puf_max_hit):
        if (t_volano >= t_puffer + puf_delta_start) and (t_volano >= vol_min_puf + vol_h_puf):
            volano_to_puffer = True
        elif last_vol_to_puf and (t_volano >= t_puffer + puf_delta_hold) and (t_volano >= vol_min_puf):
            volano_to_puffer = True
    # Fine giornata: se ACS resta prioritaria ma nessuna sorgente riesce a prenderla,
    # scarica il calore del volano nel puffer (tipicamente più freddo) per non sprecarlo.
    evening_dump_enabled = bool(vol_cfg.get("evening_dump_enabled", True))
    evening_dump_after_h = _parse_hour_float(vol_cfg.get("evening_dump_after_h", 17.0), 17.0)
    evening_dump_trigger = str(vol_cfg.get("evening_dump_trigger", "time") or "time").strip().lower()
    if evening_dump_trigger not in ("time", "entity"):
        evening_dump_trigger = "time"
    evening_dump_run_entity = str(vol_cfg.get("evening_dump_run_entity", "") or "").strip()
    evening_dump_run_state = ha_states.get(evening_dump_run_entity, {}).get("state") if evening_dump_run_entity else None
    now_loc = time.localtime(now_ts)
    now_h = now_loc.tm_hour + (now_loc.tm_min / 60.0)
    if evening_dump_trigger == "entity":
        evening_window = _is_on_state(evening_dump_run_state)
    else:
        evening_window = now_h >= evening_dump_after_h
    if (
        (not volano_to_puffer)
        and volano_to_puffer_enabled
        and evening_dump_enabled
        and evening_window
        and (dest == "ACS")
        and (source_to_acs == "OFF")
        and (not puf_max_hit)
    ):
        if (t_volano >= t_puffer + puf_delta_hold) and (t_volano >= vol_min_puf):
            volano_to_puffer = True
            evening_dump_active = True
            if evening_dump_trigger == "entity":
                evening_dump_reason = (
                    f"Dump trigger da entita attivo ({evening_dump_run_entity or 'n/d'}="
                    f"{evening_dump_run_state or 'n/d'}): ACS non prendibile, scarico VOLANO->PUFFER."
                )
            else:
                evening_dump_reason = (
                    f"Fine giornata attiva (ora {now_h:.2f}h >= {evening_dump_after_h:.2f}h): "
                    f"ACS non prendibile, scarico VOLANO->PUFFER."
                )
        else:
            evening_dump_reason = (
                f"Dump attivo ma soglie non raggiunte: "
                f"T_VOL {t_volano:.1f}C | T_PUF {t_puffer:.1f}C | "
                f"d_hold {puf_delta_hold:.1f}C | Min {vol_min_puf:.1f}C"
            )
    if force_vtp_active:
        if force_vtp_can_apply:
            volano_to_puffer = True
            force_vtp_reason = (
                f"Forzatura VOLANO->PUFFER attiva ({force_vtp_remaining_s}s). "
                f"Dest={dest} | Source={source_to_acs} | T_VOL {t_volano:.1f}C | T_PUF {t_puffer:.1f}C"
            )
        else:
            force_vtp_reason = (
                f"Forzatura attiva ma non applicabile ({force_vtp_remaining_s}s): "
                f"Dest={dest} | Source={source_to_acs} | PUF_MAX={'SI' if puf_max_hit else 'NO'} | "
                f"T_VOL {t_volano:.1f}C | T_PUF {t_puffer:.1f}C"
            )

    battery_block_w = float(res_cfg.get("battery_block_w", 100.0))
    export_off_w = float(res_cfg.get("export_off_w", -100.0))
    last_base = _LAST.get("res_base")
    if export_w > extra_safe_w:
        effective_power_w = max(0.0, export_w + res_power_w)
        base_sel = "export"
    elif last_base == "export" and res_power_w > 0.0:
        effective_power_w = max(0.0, export_w + res_power_w)
        base_sel = "export"
    else:
        # If resistances are already on, add their power to available
        # to avoid getting stuck below the next step threshold.
        effective_power_w = extra_safe_w + (res_power_w if res_power_w > 0.0 else 0.0)
        base_sel = "possibile"

    desired_step = 0
    resistance_enabled = resistenze_enabled and res_cfg.get("enabled", True)
    if dest in ("ACS", "PUFFER") and (not vol_max_hit) and resistance_enabled:
        if battery_output_w > battery_block_w:
            desired_step = 0
        elif export_w <= export_off_w:
            desired_step = 0
        elif effective_power_w <= 0.0:
            desired_step = 0
        else:
            thr = _thr_list(res_cfg.get("thresholds_w", [1100, 2200, 3300]))
            if effective_power_w >= thr[2]:
                desired_step = 3
            elif effective_power_w >= thr[1]:
                desired_step = 2
            elif effective_power_w >= thr[0]:
                desired_step = 1

    off_thr = float(res_cfg.get("off_threshold_w", 0.0))
    step_up_delay = int(_f(res_cfg.get("step_up_delay_s", 10), 10))
    off_delay = int(_f(res_cfg.get("off_delay_s", 5), 5))
    step_down_delay = int(_f(res_cfg.get("step_down_delay_s", off_delay), off_delay))
    last_step = int(_LAST.get("res_step", 0) or 0)
    last_step_ts = float(_LAST.get("res_step_ts", 0.0) or 0.0)
    if not resistance_enabled:
        step = 0
    elif desired_step > last_step:
        if now_ts - last_step_ts >= step_up_delay:
            step = min(desired_step, last_step + 1)
        else:
            step = last_step
    elif desired_step < last_step:
        if now_ts - last_step_ts >= step_down_delay:
            step = max(desired_step, last_step - 1)
        else:
            step = last_step
    else:
        step = last_step

    charge_buffer = "RESISTANCE" if step > 0 else "OFF"
    power_note = f"Export {export_w:.0f}W"
    if extra_safe_total_w > 0.0 or extra_safe_w > 0.0 or pv_power_w > 0.0:
        power_note = (
            f"Avail {available_w:.0f}W (Export {export_w:.0f}W | "
            f"Tot {extra_safe_total_w:.0f}W | Poss {extra_safe_w:.0f}W | FV {pv_power_w:.0f}W)"
        )
    if not resistance_enabled:
        charge_reason = f"{power_note} | Modulo resistenze OFF"
    elif vol_max_hit:
        charge_reason = f"VOLANO_MAX: {t_volano:.1f}°C >= {vol_max:.1f}°C"
    elif dest == "OFF":
        charge_reason = dest_reason
    elif battery_output_w > battery_block_w:
        charge_reason = f"{power_note} | battery_out {battery_output_w:.0f}W > {battery_block_w:.0f}W"
    elif export_w <= export_off_w or effective_power_w <= 0.0:
        charge_reason = f"{power_note} <= OFF {off_thr:.0f}W | off_delay {off_delay}s | step_up_delay {step_up_delay}s"
    else:
        charge_reason = f"{power_note} | off_delay {off_delay}s | step_up_delay {step_up_delay}s"

    _LAST["dest"] = dest
    _LAST["source_to_acs"] = source_to_acs
    _LAST["volano_to_puffer"] = volano_to_puffer
    if step != last_step:
        _LAST["res_step_ts"] = now_ts
    _LAST["res_step"] = step
    if 'base_sel' in locals():
        _LAST["res_base"] = base_sel
    _LAST["heater_easas"] = bool(easas_heater.get("on"))
    _LAST["heater_privato"] = bool(privato_heater.get("on"))

    timers_cfg = cfg.get("timers", {})
    vta_start = int(timers_cfg.get("volano_to_acs_start_s", 5))
    vta_stop = int(timers_cfg.get("volano_to_acs_stop_s", 2))
    vtp_start = int(timers_cfg.get("volano_to_puffer_start_s", 5))
    vtp_stop = int(timers_cfg.get("volano_to_puffer_stop_s", 2))
    volano_to_acs_reason = (
        f"Dest={dest} | ACS_MAX={'SI' if acs_max_hit else 'NO'} | "
        f"Source={source_to_acs} | T_VOL {t_volano:.1f}C | T_ACS {t_acs:.1f}C | "
        f"d_start {delta_start:.1f}C / d_hold {delta_hold:.1f}C | "
        f"Min {vol_min_acs:.1f}C (+{vol_h_acs:.1f}C) | "
        f"Delay start {vta_start}s / stop {vta_stop}s | "
        f"LastSource={last_source or 'None'}"
    )
    volano_to_puffer_reason = (
        f"Dest={dest} | PUF_MAX={'SI' if puf_max_hit else 'NO'} | "
        f"T_VOL {t_volano:.1f}C | T_PUF {t_puffer:.1f}C | "
        f"d_start {puf_delta_start:.1f}C / d_hold {puf_delta_hold:.1f}C | "
        f"Min {vol_min_puf:.1f}C (+{vol_h_puf:.1f}C) | "
        f"Delay start {vtp_start}s / stop {vtp_stop}s | "
        f"LastVolToPuf={'SI' if last_vol_to_puf else 'NO'} | "
        f"DumpMode={evening_dump_trigger} | "
        f"DumpAfter {evening_dump_after_h:.2f}h | DumpNow={'SI' if evening_dump_active else 'NO'} | "
        f"ForceNow={'SI' if force_vtp_active and force_vtp_can_apply else 'NO'}"
    )
    if evening_dump_reason:
        volano_to_puffer_reason = f"{volano_to_puffer_reason} | {evening_dump_reason}"
    res_blockers: list[str] = []
    if not resistance_enabled:
        res_blockers.append("Modulo OFF")
    if dest not in ("ACS", "PUFFER"):
        res_blockers.append(f"Dest={dest}")
    if vol_max_hit:
        res_blockers.append("VOL_MAX")
    if battery_output_w > battery_block_w:
        res_blockers.append(f"BatteryOut>{battery_block_w:.0f}W")
    if export_w <= export_off_w:
        res_blockers.append(f"Export<={export_off_w:.0f}W")
    if effective_power_w <= 0.0:
        res_blockers.append("PotenzaEff<=0W")
    res_diag = (
        f"stato={'ATTIVO' if step > 0 else 'OFF'} | base={base_sel} | "
        f"eff={effective_power_w:.0f}W | step={step} | blocchi={','.join(res_blockers) if res_blockers else 'nessuno'}"
    )
    transfer_diag = f"Decisione: Dest={dest} ({dest_reason}) | Source={source_to_acs} ({source_reason})"

    ent_cfg = cfg.get("entities", {})
    imp_cfg = cfg.get("impianto", {})
    sel_eid = ent_cfg.get("hvac_riscaldamento_select")
    req_eid = ent_cfg.get("richiesta_heat_piani")
    pdc_eid = ent_cfg.get("source_pdc_ready")
    vol_eid = ent_cfg.get("source_volano_ready")

    sel_state = ha_states.get(sel_eid, {}).get("state") if sel_eid else imp_cfg.get("source_mode", "AUTO")
    req_state = ha_states.get(req_eid, {}).get("state") if req_eid else ("on" if imp_cfg.get("richiesta_heat") else "off")
    pdc_ready = pdc_enabled and _is_on_state(ha_states.get(pdc_eid, {}).get("state") if pdc_eid else ("on" if imp_cfg.get("pdc_ready") else "off"))
    vol_ready = pdc_enabled and _is_on_state(ha_states.get(vol_eid, {}).get("state") if vol_eid else ("on" if imp_cfg.get("volano_ready") else "off"))
    pdc_vol_ready = pdc_enabled and (pdc_ready or vol_ready)
    puf_ready = _is_on_state(ha_states.get(ent_cfg.get("source_puffer_ready"), {}).get("state")) if ent_cfg.get("source_puffer_ready") else bool(imp_cfg.get("puffer_ready", True))
    # richiesta: se esiste un'entitÃ , usa quella; altrimenti deriva dai termostati
    zones_pt = imp_cfg.get("zones_pt", []) or []
    zones_p1 = imp_cfg.get("zones_p1", []) or []
    zones_mans = imp_cfg.get("zones_mans", []) or []
    zones_lab = imp_cfg.get("zones_lab", []) or []
    zone_scala = imp_cfg.get("zone_scala") or ""
    zones_configured = bool(zones_pt or zones_p1 or zones_mans or zones_lab or zone_scala)
    cooling_blocked = set(imp_cfg.get("cooling_blocked", []))
    def _is_zone_on(eid: str) -> bool:
        st = ha_states.get(eid, {})
        return _zone_active(st.get("state"), st.get("attributes", {}).get("hvac_action"), eid in cooling_blocked)
    any_active = any(_is_zone_on(z) for z in (zones_pt + zones_p1 + zones_mans + zones_lab + ([zone_scala] if zone_scala else [])))
    if req_eid:
        zone_demand_on = _is_on_state(req_state)
    else:
        zone_demand_on = any_active if zones_configured else bool(imp_cfg.get("richiesta_heat"))
    if zones_configured:
        zone_demand_on = any_active
    season_mode = str(imp_cfg.get("season_mode", "winter")).lower()
    sel_norm = str(sel_state or "AUTO").strip().upper()
    vol_min = float(imp_cfg.get("volano_min_c", 35.0))
    vol_on_h = float(imp_cfg.get("volano_on_hyst_c", imp_cfg.get("volano_hyst_c", 2.0)))
    vol_off_h = float(imp_cfg.get("volano_off_hyst_c", imp_cfg.get("volano_hyst_c", 2.0)))
    puf_min = float(imp_cfg.get("puffer_min_c", 35.0))
    puf_on_h = float(imp_cfg.get("puffer_on_hyst_c", imp_cfg.get("puffer_hyst_c", 2.0)))
    puf_off_h = float(imp_cfg.get("puffer_off_hyst_c", imp_cfg.get("puffer_hyst_c", 2.0)))
    vol_ok_start = t_volano >= (vol_min + vol_on_h)
    vol_ok_hold = t_volano > (vol_min - vol_off_h)
    puf_ok_start = t_puffer >= (puf_min + puf_on_h)
    puf_ok_hold = t_puffer > (puf_min - puf_off_h)
    last_imp_source = _LAST.get("impianto_source")
    vol_ok = vol_ok_start or (vol_ok_hold and last_imp_source == "PDC")
    puf_ok = puf_ok_start or (puf_ok_hold and last_imp_source == "PUFFER")

    if sel_norm not in ("AUTO", "PDC", "PUFFER"):
        sel_norm = "AUTO"
    # IMPIANTO_LOGIC: richiesta ON se una sorgente valida e' disponibile.
    # Le zone attive guidano uscite/pompe, non la disponibilita' fonte.
    if sel_norm == "PDC":
        source_req_on = bool(pdc_vol_ready and vol_ok)
    elif sel_norm == "PUFFER":
        source_req_on = bool(puf_ready and puf_ok)
    else:
        source_req_on = bool((pdc_vol_ready and vol_ok) or (puf_ready and puf_ok))
    req_on = bool(impianto_enabled and source_req_on)
    if season_mode == "summer":
        req_on = False

    acs_volano_active = source_to_acs == "VOLANO"
    source_override = False
    if acs_volano_active:
        if puf_ready and puf_ok:
            source = "PUFFER"
        else:
            source = "OFF"
        source_override = True

    if not impianto_enabled:
        source = "OFF"
    elif not source_override:
        if sel_norm == "AUTO" or (
            (sel_norm == "PDC" and (not pdc_vol_ready or not vol_ok)) or
            (sel_norm == "PUFFER" and (not puf_ready or not puf_ok))
        ):
            if pdc_vol_ready and vol_ok:
                source = "PDC"
            else:
                source = "PUFFER" if (puf_ready and puf_ok) else "OFF"
        else:
            source = sel_norm if (
                (sel_norm == "PDC" and vol_ok) or
                (sel_norm == "PUFFER" and puf_ok)
            ) else "OFF"
    _LAST["impianto_source"] = source if source in ("PDC", "PUFFER") else None
    def _float_list(val, default_list):
        if isinstance(val, (list, tuple)):
            out = []
            for v in val:
                try:
                    out.append(float(v))
                except Exception:
                    continue
            if out:
                return out
        return list(default_list)

    def _interp_curve(x_val, xs, ys):
        n = len(xs)
        if n == 0 or len(ys) != n:
            return None
        x_min = min(xs)
        x_max = max(xs)
        if x_val <= x_min:
            for i in range(n):
                if xs[i] == x_min:
                    return ys[i]
            return ys[0]
        if x_val >= x_max:
            for i in range(n):
                if xs[i] == x_max:
                    return ys[i]
            return ys[-1]
        for i in range(n - 1):
            xi = xs[i]
            xj = xs[i + 1]
            yi = ys[i]
            yj = ys[i + 1]
            if (xi <= x_val <= xj) or (xj <= x_val <= xi):
                if xj == xi:
                    return yi
                return yi + ((yj - yi) * ((x_val - xi) / (xj - xi)))
        return ys[0]

    default_x = [-15, -11.25, -7.5, -3.75, 0, 3.75, 7.5, 11.25, 15]
    default_y = [60, 57.6, 55, 52.6, 50, 47.6, 45, 42.6, 40]
    curve_x = _float_list(curve_cfg.get("x"), default_x)
    curve_y = _float_list(curve_cfg.get("y"), default_y)
    if len(curve_x) != len(curve_y) or len(curve_x) < 2:
        curve_x = list(default_x)
        curve_y = list(default_y)
    curve_slope = float(curve_cfg.get("slope", 0.0))
    curve_offset = float(curve_cfg.get("offset", 0.0))
    curve_min = float(curve_cfg.get("min_c", 40.0))
    curve_max = float(curve_cfg.get("max_c", 60.0))

    curve_base = None
    curve_setpoint = None
    if curve_enabled and t_esterna is not None:
        curve_base = _interp_curve(float(t_esterna), curve_x, curve_y)
        if curve_base is not None:
            y_avg = sum(curve_y) / len(curve_y)
            mod = y_avg + (1.0 + curve_slope) * (curve_base - y_avg) + curve_offset
            curve_setpoint = max(curve_min, min(curve_max, mod))

    mix_sp = get_num(ent.get("miscelatrice_setpoint"), float(misc_cfg.get("setpoint_c", 45.0)))
    if curve_enabled and curve_setpoint is not None:
        mix_sp = float(curve_setpoint)
    elif curve_enabled and t_esterna is None:
        # Requested fallback: if external temperature is unavailable, use 45°C.
        mix_sp = 45.0
    mix_h = float(misc_cfg.get("hyst_c", 0.5))
    mix_dt_ref = float(misc_cfg.get("dt_ref_c", 10.0))
    mix_dt_min_f = float(misc_cfg.get("dt_min_factor", 0.6))
    mix_dt_max_f = float(misc_cfg.get("dt_max_factor", 1.4))
    mix_dt = max(0.0, t_mandata_mix - t_ritorno_mix)
    mix_kp_eff = float(misc_cfg.get("kp", 2.0))
    if mix_dt_ref > 0:
        mix_kp_eff = mix_kp_eff * max(mix_dt_min_f, min(mix_dt_max_f, mix_dt / mix_dt_ref))
    mix_enabled = miscelatrice_enabled
    mix_action = "STOP"
    mix_reason = "Miscelatrice non attiva."
    mix_delay_info = f"pause {int(misc_cfg.get('pause_s', 5))}s | min_imp {int(misc_cfg.get('min_imp_s', 1))}s | max_imp {int(misc_cfg.get('max_imp_s', 8))}s"
    if mix_enabled:
        if gas_enabled:
            mix_action = "ALZA"
            mix_reason = f"Gas attivo: miscelatrice ALZA fissa. | {mix_delay_info}"
        else:
            err = mix_sp - t_mandata_mix
            if abs(err) <= mix_h:
                mix_reason = f"Delta entro isteresi. | {mix_delay_info}"
            elif err > 0:
                mix_action = "ALZA"
                mix_reason = f"T_MAND {t_mandata_mix:.1f}°C < SP {mix_sp:.1f}°C | dT {mix_dt:.1f}°C | KpEff {mix_kp_eff:.2f} | {mix_delay_info}"
            else:
                mix_action = "ABBASSA"
                mix_reason = f"T_MAND {t_mandata_mix:.1f}°C > SP {mix_sp:.1f}°C | dT {mix_dt:.1f}°C | KpEff {mix_kp_eff:.2f} | {mix_delay_info}"

    blocked_cold = req_on and (source == "OFF")
    imp_active = impianto_enabled and req_on and zone_demand_on and (source != "OFF") and (not blocked_cold) and (not gas_enabled)
    miscelatrice_on = imp_active and miscelatrice_enabled
    if not miscelatrice_on:
        mix_action = "STOP"
        if gas_enabled:
            mix_reason = f"Impianto inattivo. Alza fisso per caldaia a GAS emergenza. | {mix_delay_info}"
        else:
            mix_reason = f"Impianto inattivo. | {mix_delay_info}"

    pump_start_delay = int(imp_cfg.get("pump_start_delay_s", 9))
    pump_stop_delay = int(imp_cfg.get("pump_stop_delay_s", 0))
    auto_heat_min_on = int(imp_cfg.get("auto_heat_min_on_s", 60))
    auto_heat_min_off = int(imp_cfg.get("auto_heat_min_off_s", 60))
    impianto_delay_info = f"pump_start {pump_start_delay}s | pump_stop {pump_stop_delay}s | auto_heat_on {auto_heat_min_on}s | auto_heat_off {auto_heat_min_off}s"

    if not impianto_enabled:
        impianto_reason = "Modulo impianto OFF."
    elif season_mode == "summer":
        impianto_reason = "Estate: riscaldamento bloccato."
    elif gas_enabled:
        impianto_reason = "Gas emergenza attivo: impianto inattivo."
    elif blocked_cold:
        impianto_reason = "Bloccato: nessuna fonte disponibile o troppo fredda."
    else:
        impianto_reason = (
            f"Richiesta={ 'ON' if req_on else 'OFF' } | Sel={sel_norm} | "
        f"PDC/VOL={'ON' if pdc_vol_ready else 'OFF'} "
        f"PUF={'ON' if puf_ready else 'OFF'} "
        f"Source={source} "
        f"| Miscelatrice={'ON' if miscelatrice_on else 'OFF'}"
        )
    if acs_volano_active:
        impianto_reason = f"{impianto_reason} | ACS da Volano: impianto {source}"
    impianto_reason = f"{impianto_reason} | {impianto_delay_info}"

    cooling_blocked = set(imp_cfg.get("cooling_blocked", []))
    gas_zones = gas_cfg.get("zones", []) if isinstance(gas_cfg.get("zones"), list) else []
    gas_zones = [str(z).strip() for z in gas_zones if str(z).strip()]
    zones_pt = set(imp_cfg.get("zones_pt", []))
    zones_p1 = set(imp_cfg.get("zones_p1", []))
    zones_mans = set(imp_cfg.get("zones_mans", []))
    zones_lab = set(imp_cfg.get("zones_lab", []))
    zone_scala = (imp_cfg.get("zone_scala") or "").strip()
    gas_active_any = False
    gas_pt = gas_p1 = gas_mans = gas_lab = gas_scala = False
    for z in gas_zones:
        st = ha_states.get(z, {})
        is_active = _zone_active(st.get("state"), st.get("attributes", {}).get("hvac_action"), z in cooling_blocked)
        gas_active_any = gas_active_any or is_active
        if z == zone_scala:
            gas_scala = gas_scala or is_active
        if z in zones_pt:
            gas_pt = gas_pt or is_active
        if z in zones_p1:
            gas_p1 = gas_p1 or is_active
        if z in zones_mans:
            gas_mans = gas_mans or is_active
        if z in zones_lab:
            gas_lab = gas_lab or is_active

    gas_vol_min = float(gas_cfg.get("volano_min_c", 35.0))
    gas_vol_h = float(gas_cfg.get("volano_hyst_c", 2.0))
    gas_puf_min = float(gas_cfg.get("puffer_min_c", 35.0))
    gas_puf_h = float(gas_cfg.get("puffer_hyst_c", 2.0))
    gas_vol_prev = bool(_LAST.get("gas_vol_ok"))
    gas_puf_prev = bool(_LAST.get("gas_puf_ok"))
    if t_volano is None:
        gas_vol_ok = True
    else:
        gas_vol_ok = t_volano > gas_vol_min if gas_vol_prev else t_volano >= (gas_vol_min + gas_vol_h)
    if t_puffer is None:
        gas_puf_ok = True
    else:
        gas_puf_ok = t_puffer > gas_puf_min if gas_puf_prev else t_puffer >= (gas_puf_min + gas_puf_h)
    _LAST["gas_vol_ok"] = gas_vol_ok
    _LAST["gas_puf_ok"] = gas_puf_ok
    gas_need = bool(gas_enabled and (not (gas_vol_ok or gas_puf_ok)))
    gas_reason = "Modulo gas OFF."
    if gas_enabled:
        if gas_need:
            gas_reason = f"Gas attivo: domanda={'ON' if gas_active_any else 'OFF'} | VOL_OK={gas_vol_ok} PUF_OK={gas_puf_ok}"
        else:
            gas_reason = "Gas standby: fonte principale disponibile."
    gas_reason = f"{gas_reason} | min_on {int(gas_cfg.get('min_on_s', 120))}s | min_off {int(gas_cfg.get('min_off_s', 120))}s"

    legna_min = float(legna_cfg.get("temp_min_alim_c", 35.0))
    legna_min_hyst = float(legna_cfg.get("temp_min_alim_hyst_c", 5.0))
    legna_sp_puf = float(legna_cfg.get("puffer_alto_sp_c", 80.0))
    legna_puf_hyst = float(legna_cfg.get("puffer_alto_hyst_c", 3.0))
    legna_startup_s = int(legna_cfg.get("startup_check_s", 600))
    legna_forced_off = bool(legna_cfg.get("forced_off", False))
    if not legna_enabled:
        legna_reason = "Modulo legna OFF."
        legna_power = False
        legna_ta = False
    elif legna_forced_off:
        legna_reason = "Timer scaduto: modulo inattivo."
        legna_power = False
        legna_ta = False
    else:
        if t_mandata_legna is None:
            legna_reason = f"Sonda mandata assente. Min {legna_min:.1f}C"
            legna_power = False
        elif t_mandata_legna < legna_min:
            legna_reason = f"Mandata bassa: {t_mandata_legna:.1f}C < {legna_min:.1f}C"
            legna_power = False
        else:
            legna_reason = f"Mandata ok: {t_mandata_legna:.1f}C >= {legna_min:.1f}C"
            legna_power = True
        legna_ta = bool(t_puffer_alto < legna_sp_puf) if t_puffer_alto is not None else False
    legna_reason = f"{legna_reason} | startup_check {legna_startup_s}s"

    return {
            "inputs": {
            "t_acs": t_acs,
            "t_acs_alto": t_acs_alto,
            "t_acs_medio": t_acs_medio,
            "t_acs_basso": t_acs_basso,
            "t_puffer": t_puffer,
            "t_puffer_alto": t_puffer_alto,
            "t_puffer_medio": t_puffer_medio,
            "t_puffer_basso": t_puffer_basso,
            "t_volano": t_volano,
            "t_volano_alto": t_volano_alto,
            "t_volano_basso": t_volano_basso,
            "t_solare_mandata": t_sol,
            "solare_flow_lmin": sol_flow,
            "collettore_status_code": col_status_code,
            "collettore_status": col_status,
            "collettore_datetime": col_datetime,
            "collettore_energy_day_kwh": col_energy_day,
            "collettore_energy_total_kwh": col_energy_total,
            "collettore_flow_lmin": col_flow,
            "collettore_pwm_pct": col_pwm,
            "collettore_status2": col_status2,
            "collettore_temp_esterna": col_t_ext,
            "collettore_tsa1": col_tsa1,
            "collettore_tse": col_tse,
            "collettore_tsv": col_tsv,
            "collettore_twu": col_twu,
            "t_esterna": t_esterna,
            "t_mandata_miscelata": t_mandata_mix,
            "t_ritorno_miscelato": t_ritorno_mix,
            "grid_export_w": export_w,
            "extra_safe_w": extra_safe_w,
            "extra_safe_total_w": extra_safe_total_w,
            "battery_output_w": battery_output_w,
            "battery_temp_c": battery_temp_c,
            "pv_power_w": pv_power_w,
            "battery_temp_c_easas": battery_temp_c_easas,
            "battery_temp_c_privato": battery_temp_c_privato,
            "battery_soc_easas": battery_soc_easas,
            "battery_soc_privato": battery_soc_privato,
            "grid_export_w_easas": export_w_easas,
            "grid_export_w_privato": export_w_privato,
            "battery_output_w_easas": batt_out_easas,
            "battery_output_w_privato": batt_out_privato,
            "pv_power_w_easas": pv_power_easas,
            "pv_power_w_privato": pv_power_privato,
            "resistenze_volano_power": res_power_w,
            "t_mandata_caldaia_legna": t_mandata_legna,
            "t_ritorno_caldaia_legna": t_ritorno_legna,
            "t_caldaia_legna": t_caldaia_legna
        },
            "computed": {
                "available_power_w": available_w,
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
            "impianto": {
                "source": source,
                "richiesta": req_on,
                "zone_demand": zone_demand_on,
                "zones_active": any_active,
                "miscelatrice": miscelatrice_on,
                "pdc_ready": pdc_vol_ready,
                "volano_ready": vol_ready,
                "puffer_ready": puf_ready,
                "volano_temp_ok": bool(vol_ok),
                "puffer_temp_ok": bool(puf_ok),
                "volano_min_c": vol_min,
                "volano_on_hyst_c": vol_on_h,
                "volano_off_hyst_c": vol_off_h,
                "volano_start_c": vol_min + vol_on_h,
                "volano_hold_c": vol_min - vol_off_h,
                "puffer_min_c": puf_min,
                "puffer_on_hyst_c": puf_on_h,
                "puffer_off_hyst_c": puf_off_h,
                "puffer_start_c": puf_min + puf_on_h,
                "puffer_hold_c": puf_min - puf_off_h,
                "blocked_cold": blocked_cold,
                "reason": impianto_reason,
                "selector": sel_norm
            },
            "force_acs_puffer": {
                "active": force_active,
                "until_ts": force_until,
                "remaining_s": force_remaining_s,
                "can_apply": force_can_apply,
                "reason": force_reason
            },
            "force_volano_puffer": {
                "active": force_vtp_active,
                "until_ts": force_vtp_until,
                "remaining_s": force_vtp_remaining_s,
                "can_apply": force_vtp_can_apply,
                "reason": force_vtp_reason
            },
            "miscelatrice": {
                "enabled": mix_enabled,
                "setpoint": mix_sp,
                "hyst": mix_h,
                "t_mandata": t_mandata_mix,
                "t_ritorno": t_ritorno_mix,
                "delta_tr": mix_dt,
                "kp_eff": mix_kp_eff,
                "action": mix_action,
                "reason": mix_reason
            },
            "energy_easas": {
                "extra_safe_w": easas["extra_safe_w"],
                "extra_safe_total_w": easas["extra_safe_total_w"],
                "max_charge_w": easas["max_charge_w"],
                "headroom_w": easas["headroom_w"],
                "temp_c": easas["temp_c"],
                "soc_pct": easas.get("soc_pct"),
                "export_w": easas["export_w"],
                "battery_output_w": easas["battery_output_w"]
            },
            "energy_privato": {
                "extra_safe_w": privato["extra_safe_w"],
                "extra_safe_total_w": privato["extra_safe_total_w"],
                "max_charge_w": privato["max_charge_w"],
                "headroom_w": privato["headroom_w"],
                "temp_c": privato["temp_c"],
                "soc_pct": privato.get("soc_pct"),
                "export_w": privato["export_w"],
                "battery_output_w": privato["battery_output_w"]
            },
            "energy_heater": {
                "easas": easas_heater,
                "privato": privato_heater
            },
            "curva_climatica": {
                "enabled": curve_enabled,
                "t_ext": t_esterna,
                "base": curve_base,
                "setpoint": curve_setpoint,
                "slope": curve_slope,
                "offset": curve_offset,
                "min_c": curve_min,
                "max_c": curve_max,
                "x": curve_x,
                "y": curve_y
            },
            "gas_emergenza": {
                "enabled": gas_enabled,
                "need": gas_need,
                "vol_ok": gas_vol_ok,
                "puf_ok": gas_puf_ok,
                "demand": gas_active_any,
                "pt": gas_pt,
                "p1": gas_p1,
                "mans": gas_mans,
                "lab": gas_lab,
                "scala": gas_scala
            },
        "caldaia_legna": {
                "enabled": legna_enabled,
                "power": legna_power,
                "ta": legna_ta,
                "t_mandata": t_mandata_legna,
                "t_puffer_alto": t_puffer_alto,
                "min_alim": legna_min,
                "min_alim_hyst": legna_min_hyst,
                "sp_puffer_alto": legna_sp_puf,
                "puffer_hyst": legna_puf_hyst,
                "reason": legna_reason
            },
            "module_reasons": {
                "solare": (
                    f"{transfer_diag} | {source_reason} | T_SOL {t_sol:.1f}C | T_ACS {t_acs:.1f}C | Flow {sol_flow:.1f} l/min (min {flow_min_lmin:.1f}) | d_on {solar_delta_on:.1f}C / d_hold {solar_delta_hold:.1f}C | pv_debounce {int(solar_cfg.get('pv_debounce_s', 300))}s"
                    if source_to_acs == "SOLAR"
                    else f"Solare non attivo. {transfer_diag} | T_SOL {t_sol:.1f}C | T_ACS {t_acs:.1f}C | Flow {sol_flow:.1f} l/min (min {flow_min_lmin:.1f}) | d_on {solar_delta_on:.1f}C / d_hold {solar_delta_hold:.1f}C | pv_debounce {int(solar_cfg.get('pv_debounce_s', 300))}s"
                ),
                "volano_to_acs": (
                    f"{transfer_diag} | {volano_to_acs_reason}"
                    if source_to_acs == "VOLANO"
                    else f"Volano -> ACS non attivo. {transfer_diag} | {volano_to_acs_reason}"
                ),
                "puffer_to_acs": (
                    f"{transfer_diag} | {source_reason} | T_PUF {t_puffer:.1f}C | T_ACS {t_acs:.1f}C | d_start {puf_to_acs_start:.1f}C / d_hold {puf_to_acs_hold:.1f}C | Min {puf_min_acs:.1f}C (+{puf_h_acs:.1f}C)"
                    if source_to_acs == "PUFFER"
                    else f"Puffer -> ACS non attivo. {transfer_diag} | T_PUF {t_puffer:.1f}C | T_ACS {t_acs:.1f}C | d_start {puf_to_acs_start:.1f}C / d_hold {puf_to_acs_hold:.1f}C | Min {puf_min_acs:.1f}C (+{puf_h_acs:.1f}C)"
                ),
                "volano_to_puffer": (
                    f"{transfer_diag} | {volano_to_puffer_reason}"
                    if volano_to_puffer
                    else f"Volano -> Puffer non attivo. {transfer_diag} | {volano_to_puffer_reason}"
                ),
                "curva_climatica": (
                    f"T_EXT {t_esterna:.1f}C -> SP {curve_setpoint:.1f}C"
                    if curve_enabled and curve_setpoint is not None and t_esterna is not None
                    else ("T_EXT n/d -> fallback SP 45.0C" if curve_enabled and t_esterna is None else "Curva climatica non attiva.")
                ),
                "resistenze_volano": f"{transfer_diag} | {charge_reason} | {res_diag} | {power_note}",
                "energy_easas": f"Extra {easas['extra_safe_w']:.0f}W | Tot {easas['extra_safe_total_w']:.0f}W | Headroom {easas['headroom_w']:.0f}W",
                "energy_privato": f"Extra {privato['extra_safe_w']:.0f}W | Tot {privato['extra_safe_total_w']:.0f}W | Headroom {privato['headroom_w']:.0f}W",
                "energy_heater_easas": f"ON={easas_heater['on']} | {easas_heater['reason']}",
                "energy_heater_privato": f"ON={privato_heater['on']} | {privato_heater['reason']}",
                "impianto": impianto_reason,
                "gas_emergenza": gas_reason,
                "caldaia_legna": legna_reason,
                "miscelatrice": mix_reason,
                "force_acs_puffer": force_reason,
                "force_volano_puffer": force_vtp_reason
            },
            "module_summaries": {
                "solare": "Regola: attivo se T_SOL >= T_ACS + d_on (o d_hold se già attivo).",
                "volano_to_acs": "Regola: Dest=ACS e T_VOL >= T_ACS+Δ e T_VOL >= Min.",
                "volano_to_puffer": "Regola: Dest=PUFFER e T_VOL >= T_PUF+Δ e T_VOL >= Min. Fine giornata: se Dest=ACS ma non prendibile, scarica VOLANO su PUFFER dopo orario impostato.",
                "puffer_to_acs": "Regola: Dest=ACS e T_PUF >= T_ACS+Δ e T_PUF >= Min.",
                "miscelatrice": "Regola: mantiene ΔT mandata/ritorno verso setpoint con impulsi.",
                "curva_climatica": "Regola: SP da curva in base a T_EXT.",
                "impianto": "Regola: quando c'e una fonte calda disponibile, i termostati restano in HEAT. L'impianto parte solo sopra la soglia di avvio; se era gia partito, continua fino alla soglia di mantenimento piu bassa. Pompe e valvole si attivano solo con zone attive.",
                "gas_emergenza": "Regola: gas attivo se zone richiedono e sorgenti fredde.",
                "caldaia_legna": "Regola: mandata >= min e puffer < SP.",
                "resistenze_volano": "Regola: base Export se Export>Possibile o se resistenze ON da Export; altrimenti Possibile. Export + resistenze. Export < -100W OFF secco; batteria scarica step-down.",
                "force_acs_puffer": "Regola: forzatura temporizzata ACS da PUFFER senza cambiare setpoint.",
                "force_volano_puffer": "Regola: forzatura temporizzata VOLANO->PUFFER o dump automatico (orario/entita RUN) quando ACS e prioritaria ma non prendibile."
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


