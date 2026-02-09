# e-ThermoMind — Project log (estratto dalla conversazione)
Data export: 2026-02-08 (Europe/Rome)

> Nota: non posso garantire un “verbatim transcript” perfetto al 100% dell’intera chat (limiti tecnici dell’interfaccia),
> ma questo documento contiene una traccia fedele e dettagliata di decisioni, requisiti e specifiche concordate.

## Obiettivo
- Portare la logica dall’insieme di blueprint ad un Add-on HA replicabile.
- UI in **Vue**, responsive: **Admin** (config/debug) + **User** (monitoraggio; in futuro schema animato).
- HA resta I/O (sensori/switch). Setpoint/stati/logica dentro addon.

## Nome Add-on
- **e-ThermoMind**

## Architettura concordata
- Motore modulare a “state machine”:
  1) ACS Orchestrator
  2) Puffer
  3) Volano + Resistenze (FV/export)
  4) Solare (valvole + ritorni + notte/cutback)
  5) Heat Radiator (miscelatrice mandata/ritorno)
  6) PDC (2 macchine) – per ora DISABLED/standby

## Setpoint e safety
- Setpoint **interni addon**:
  - ACS_SP, PUFFER_SP
  - VOLANO_TARGET = ACS_SP + margine (scelta “2”)
- Sicurezze configurabili:
  - ACS_MAX (+ isteresi)
  - VOLANO_MAX (+ isteresi)
  - (futuro) PUFFER_MAX

## Solare “impulsivo”
- Il solare su ACS può durare pochi minuti: NON deve bloccare carica riserva.
- Possibile: SOLAR→ACS mentre si carica VOLANO (PDC/resistenze) per ripartenza.

## Regola “ACS a regime”
- Se ACS è già a regime: non accendere PDC/resistenze “per ACS”.
- In quel caso, se c’è surplus, la destinazione diventa PUFFER (accumulo giorno/notte).

## Volano → ACS / Puffer (delta termico)
- Trasferimento (valvola + pompa) parte solo se:
  - T_volano >= T_dest + Δ_start
  - continua finché T_volano >= T_dest + Δ_hold

## Resistenze su export rete
- 3×1000W su volano.
- Step in base a export (immissione), con OFF delay 5s per evitare attacca/stacca.
- Condizionate dalla destinazione: ACS (se non a regime) o PUFFER (se ACS a regime).

## PDC
- 2 PDC (entrambe master), richiesto supporto alternanza/fallback.
- Stato attuale: non funzionanti → modulo PDC DISABLED in v1, attivabile da Admin quando pronte.

## Aggiornamenti 2026-02-08
- Fix encoding/charset in `config.yaml`, `web/index.html`, `web/src/App.vue`, `backend/logic.py`.
- UI Admin estesa per mapping entità HA + reload rapido.
- API backend aggiunte: `/api/entities` GET/POST.
- Validazione base payload e normalizzazione config/setpoint.
- Guardie su `thresholds_w` + formatting output decisioni.
- WS HA con reconnect/backoff e logging minimo.

## Aggiornamenti 2026-02-09
- Resistenze volano LIVE con off-delay, runtime mode UI (dry-run/live) e log azioni.
- Mapping completo attuatori R1–R30 + indicatori logica/presenza e icone HA.
- Moduli togglable in User/Admin con PIN opzionale.
- Export/Import configurazione e pulsanti header; setpoint compatti.
- Polling UI controllato (stop in Admin / durante editing).
- Dry-run con log simulati completi (moduli ON/OFF/DISABLED).
- Moduli ON evidenziati in rosso trasparente.
- Comandi manuali rimossi; toggle attuatori via pallino con bordo rosso se ON (User senza pallino).
- Header Admin: pulsanti config uniformati (stesso stile/colore) e duplicazione rimossa.
- Guard HA: se un attuatore viene acceso da HA mentre il modulo è attivo, auto spegnimento dopo 2s (UI esclusa).

## Prossime implementazioni
- Validazione completa via schema (Pydantic) per `config`/`entities`/`setpoints`.
- Persistenza configurazione per `runtime.mode` e future azioni live.
- Motori logici modulari (ACS/Puffer/Volano/Solare/PDC) con state machine separata.
- Ingress UI: sezione stato attuatori + wiring per comandi live (v0.2+).
