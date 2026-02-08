import asyncio
import logging
import os
from pathlib import Path
from typing import Any, Dict, Optional

import aiohttp

class HAClient:
    def __init__(self):
        self._token = self._load_token()
        self._ws_url = "http://supervisor/core/api/websocket"
        self._http_url = "http://supervisor/core/api"
        self._session: Optional[aiohttp.ClientSession] = None
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self.states: Dict[str, Dict[str, Any]] = {}
        self._log = logging.getLogger("ha_client")
        self.enabled = bool(self._token)

    def _load_token(self) -> Optional[str]:
        env_token = os.environ.get("SUPERVISOR_TOKEN") or os.environ.get("HASSIO_TOKEN")
        if env_token:
            return env_token
        secret_path = Path("/run/secrets/supervisor_token")
        if secret_path.exists():
            try:
                return secret_path.read_text(encoding="utf-8").strip()
            except Exception:
                return None
        return None

    async def start(self):
        if not self._token:
            self._log.warning("Missing SUPERVISOR_TOKEN / HASSIO_TOKEN; running in standalone mode.")
            self.enabled = False
            return
        self._session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self._token}", "Content-Type": "application/json"}
        )
        await self._connect_ws()

    async def close(self):
        if self._ws is not None:
            await self._ws.close()
        if self._session is not None:
            await self._session.close()

    async def _connect_ws(self):
        assert self._session is not None
        if self._ws is not None:
            await self._ws.close()
        self._ws = await self._session.ws_connect(self._ws_url, heartbeat=30)
        hello = await self._ws.receive_json()
        if hello.get("type") != "auth_required":
            raise RuntimeError(f"Unexpected WS hello: {hello}")
        await self._ws.send_json({"type": "auth", "access_token": self._token})
        auth_ok = await self._ws.receive_json()
        if auth_ok.get("type") != "auth_ok":
            raise RuntimeError(f"Auth failed: {auth_ok}")
        await self._ws.send_json({"id": 1, "type": "subscribe_events", "event_type": "state_changed"})
        sub_ok = await self._ws.receive_json()
        if not sub_ok.get("success", False):
            raise RuntimeError(f"Subscribe failed: {sub_ok}")
        await self._prime_states()

    async def _prime_states(self):
        assert self._session is not None
        async with self._session.get(f"{self._http_url}/states") as r:
            r.raise_for_status()
            data = await r.json()
        for st in data:
            self.states[st["entity_id"]] = st

    async def loop(self):
        if self._ws is None:
            return
        while True:
            msg = await self._ws.receive_json()
            if msg.get("type") == "event" and msg.get("event", {}).get("event_type") == "state_changed":
                ev = msg["event"]["data"]
                ent = ev.get("entity_id")
                new_state = ev.get("new_state")
                if ent and new_state:
                    self.states[ent] = new_state

    async def run(self):
        backoff = 1
        while True:
            try:
                self._log.info("Connecting to Home Assistant WS...")
                await self._connect_ws()
                self._log.info("WS connected.")
                backoff = 1
                await self.loop()
            except asyncio.CancelledError:
                raise
            except Exception as exc:
                self._log.warning("WS loop error: %s", exc)
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2, 30)
