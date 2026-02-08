import asyncio
import logging
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .storage import load_config, save_config, normalize_config, apply_setpoints, apply_entities
from .ha_client import HAClient
from .logic import compute_decision

app = FastAPI(title="e-ThermoMind", version="0.1.0")
ha = HAClient()
cfg = load_config()
ws_task: asyncio.Task | None = None

@app.on_event("startup")
async def on_startup():
    global cfg
    global ws_task
    cfg = load_config()
    logging.basicConfig(level=str(cfg.get("log_level", "info")).upper())
    await ha.start()
    if ha.enabled:
        ws_task = asyncio.create_task(ha.run())

@app.on_event("shutdown")
async def on_shutdown():
    global ws_task
    if ws_task:
        ws_task.cancel()
    await ha.close()

app.mount("/static", StaticFiles(directory="/app/static", html=True), name="static")

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
    return JSONResponse(compute_decision(cfg, ha.states))

@app.get("/api/setpoints")
async def get_setpoints():
    return JSONResponse({
        "acs": cfg.get("acs", {}),
        "puffer": cfg.get("puffer", {}),
        "volano": cfg.get("volano", {}),
        "resistance": cfg.get("resistance", {}),
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
    return JSONResponse(cfg.get("entities", {}))

@app.post("/api/entities")
async def set_entities(payload: dict):
    global cfg
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid payload")
    cfg = apply_entities(cfg, payload)
    save_config(cfg)
    return JSONResponse({"ok": True})
