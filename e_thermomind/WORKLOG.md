# Worklog — e-ThermoMind

## 2026-02-08
- Normalizzazione config e setpoint con guardie su input e defaults.
- Aggiunte API `/api/entities` GET/POST e validazioni minime payload.
- Reconnect WS Home Assistant con backoff e logging base.
- UI Admin estesa per mapping entità HA.
- Fix encoding in titoli/UI e stringhe logica.
- Aggiornato `PROJECT_LOG.md` con stato e roadmap.
- Aggiunto `build.yaml` per forzare base image `base-python` nel build add-on.
- Avvio server tramite `uvicorn` nel Dockerfile (binding su 0.0.0.0:8099).
- Abilitati `homeassistant_api` e `hassio_api` per ottenere `SUPERVISOR_TOKEN`.
- Lettura fallback del token da `/run/secrets/supervisor_token`.
- Avvio in modalità standalone se il token Supervisor non è disponibile.
- Serviti asset statici Vite da `/assets` per evitare pagina bianca.
- Endpoint debug `/api/assets` per verificare presenza file statici.
- Indicatore Online/Offline HA in UI (User/Admin) con endpoint `/api/status`.
- Supporto token HA da `options.json` con `ha_url`/`ha_token` (fallback se token Supervisor assente).
- Ricerca token Supervisor anche in `s6/container_environment` (compatibilità add-on).
