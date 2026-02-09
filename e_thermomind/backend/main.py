import asyncio
import logging
import time
from pathlib import Path
from fastapi import FastAPI, HTTPException
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
action_log: list[str] = []

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
    if ha.enabled:
        ws_task = asyncio.create_task(ha.run())

@app.on_event("shutdown")
async def on_shutdown():
    global ws_task
    if ws_task:
        ws_task.cancel()
    await ha.close()

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
        return
    act = cfg.get("actuators", {})
    r22 = act.get("r22_resistenza_1_volano_pdc")
    r23 = act.get("r23_resistenza_2_volano_pdc")
    r24 = act.get("r24_resistenza_3_volano_pdc")
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

@app.get("/api/status")
async def status():
    return JSONResponse({
        "ha_connected": bool(ha.enabled),
        "token_source": getattr(ha, "token_source", None),
        "version": APP_VERSION,
        "runtime_mode": cfg.get("runtime", {}).get("mode", "dry-run"),
    })

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
    })

@app.post("/api/setpoints")
async def set_setpoints(payload: dict):
    global cfg
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")
    cfg = apply_setpoints(cfg, payload)
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
                "attributes": st.get("attributes", {})
            }
        else:
            out[k] = {"entity_id": None, "state": None, "attributes": {}}
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
                "attributes": st.get("attributes", {})
            }
        else:
            states[k] = {"entity_id": None, "state": None, "attributes": {}}
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
    ok = await ha.call_service(entity_id, action)
    return JSONResponse({"ok": bool(ok)})
