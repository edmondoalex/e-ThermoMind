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
- UI: WebSocket per aggiornamenti live su User/Admin con merge che non sovrascrive input in editing.
- Resistenze: switch generale + sensori potenza/energia integrati (UI + logica).
- Runtime mode persistente (salvataggio automatico) + generale resistenze segue step.

## Prossime implementazioni
- Validazione completa via schema (Pydantic) per `config`/`entities`/`setpoints`.
- Persistenza configurazione per `runtime.mode` e future azioni live.
- Motori logici modulari (ACS/Puffer/Volano/Solare/PDC) con state machine separata.
- Ingress UI: sezione stato attuatori + wiring per comandi live (v0.2+).
## UI Mapping Indicators (Do Not Change)
- Dot (green/red): mapped in logic (entity_id present)
- Input border green: entity present
- Input fill red: entity state ON

## Aggiornamenti 2026-02-11
- Modulo **Caldaia Gas Emergenza** con:
  - soglie dedicate Volano/Puffer + isteresi;
  - lista termostati “gas emergenza” gestiti dal modulo;
  - attuatori `220V caldaia gas` e `TA caldaia gas`.
- Logica gas:
  - GAS attivo solo se Volano/Puffer sotto soglia;
  - termostati gas sempre forzati in `heat` quando GAS attivo;
  - TA/220V ON solo se almeno un termostato è in `heating`;
  - **R4/R5 sempre OFF** in gas.
- Valvole in gas:
  - PT/Scala → R2 + R3
  - Laboratorio → R3 + R1 + pompa lab (R11)
  - Mansarda/1P da soli → nessuna valvola (caldaia spinge con pompa interna).
- **Pompa mandata piani (R12)** mai usata in gas.
- **Miscelatrice**:
  - in gas, se PT o Lab in heating → apertura totale (ALZA fisso);
  - fuori gas → logica normale.
- Modalità normale (impianto):
  - se calore disponibile (Puffer/Volano sopra soglia) → termostati in `heat`;
  - se calore assente → termostati in `off` (risparmio testine).
- Fix vari:
  - `/api/setpoints` include `gas_emergenza`;
  - persistenza flag “Storico” per Volano Alto/Basso;
  - log “SAVE …” in Ultime azioni per setpoints/entities/actuators/modules.

## Aggiornamenti 2026-02-14
- Persistenza moduli: /api/modules salva modules_enabled su disco (prima era live-only).
- Versione add-on aggiornata a 0.6.59.


## Aggiornamenti 2026-02-14
- Toggle moduli: UI invia solo chiave/valore e backend fa merge per evitare overwrite da payload vecchi.
- Versione add-on aggiornata a 0.6.61.


## Aggiornamenti 2026-02-14
- Setpoints: /api/setpoints non sovrascrive piu modules_enabled (restano gestiti da /api/modules, salvo blocco stagionale).
- Versione add-on aggiornata a 0.6.62.


## Aggiornamenti 2026-02-14
- Resistenze volano: se modulo OFF, non forza piu lo spegnimento (controllo manuale da HA).
- Versione add-on aggiornata a 0.6.63.


## Aggiornamenti 2026-02-18
- Watchdog impianto: logga stati incoerenti (no source/no demand con attuatori o zone ON), senza modificare la logica.
- Versione add-on aggiornata a 0.6.64.


## Aggiornamenti 2026-02-18
- Impianto: isteresi separate ON/OFF per volano e puffer (salita/discesa).
- Watchdog (solo log) estesi a resistenze, solare, miscelatrice, volano, gas, legna.
- Versione add-on aggiornata a 0.6.66.


## Aggiornamenti 2026-02-18
- User: slider rapidi per setpoint Volano/Puffer/Impianto + select Stagione con salvataggio immediato.
- Versione add-on aggiornata a 0.6.67.


## Aggiornamenti 2026-02-18
- Solare: precedenza ACS attiva sempre quando T_SOL >= T_ACS+delta (fino ad ACS_MAX), indipendente da dest.
- Versione add-on aggiornata a 0.6.68.


## Aggiornamenti 2026-02-18
- User: slider ACS setpoint e ACS MAX con salvataggio immediato.
- Versione add-on aggiornata a 0.6.69.


## Aggiornamenti 2026-02-18
- UI User: sezione Watchdog con elenco filtrato (data + motivazione).
- Versione add-on aggiornata a 0.6.70.


## Aggiornamenti 2026-02-18
- UI User: badge lampeggiante ? ATTENZIONE: WATCHDOG se presenti eventi.
- Versione add-on aggiornata a 0.6.71.


## Aggiornamenti 2026-02-18
- UI User: pulsante Reset watchdog per azzerare la lista visibile.
- Versione add-on aggiornata a 0.6.72.


## Aggiornamenti 2026-02-18
- Impianto: log espliciti quando viene saltato per gas emergenza e quando spegne per no_source/no_demand.
- Versione add-on aggiornata a 0.6.73.


## Aggiornamenti 2026-02-18
- Zone active: ora contano solo hvac_action heating/cooling (idle non attivo).
- Versione add-on aggiornata a 0.6.74.


## Aggiornamenti 2026-02-18
- Zone active: off/idle non conta anche per gas emergenza (richiesta solo se state!=off e hvac_action=heating).
- Versione add-on aggiornata a 0.6.75.


## Aggiornamenti 2026-02-18
- Impianto: hold puffer/volano applicato con domanda anche senza last_source (evita stop a min+ON dopo restart).
- Versione add-on aggiornata a 0.6.76.


## Aggiornamenti 2026-02-18
- Impianto: inizializzazione di `demand_on` per evitare UnboundLocalError in `_apply_impianto_live`.
- Versione add-on aggiornata a 0.6.77.


## Aggiornamenti 2026-02-18
- Impianto: force OFF valvole/pompe quando inattivo (no_source/no_demand) e log motivi ON/OFF.
- Versione add-on aggiornata a 0.6.78.


## Aggiornamenti 2026-02-18
- Impianto: decisione UI allineata alla logica live (isteresi ON/OFF con domanda).
- Versione add-on aggiornata a 0.6.79.


## Aggiornamenti 2026-02-18
- Impianto: dopo GAS OFF riparte solo con isteresi ON (start_only finché la sorgente è valida).
- Versione add-on aggiornata a 0.6.80.


## Aggiornamenti 2026-02-18
- UI: badge watchdog non lampeggia più per permettere la lettura.
- Versione add-on aggiornata a 0.6.81.


## Aggiornamenti 2026-02-19
- Log: de-dup azioni ripetute (stesso messaggio entro 5s aggiorna timestamp).
- Versione add-on aggiornata a 0.6.82.


## Aggiornamenti 2026-02-19
- Scheduler: pagina settimanale gas ON, timeline e persistenza.
- UI: header allineato allo stile richiesto.
- Versione add-on aggiornata a 0.6.83.


## Aggiornamenti 2026-02-19
- Fix: ripristinata funzione `_get_num` dopo inserimento scheduler (crash avvio).
- Versione add-on aggiornata a 0.6.84.


## Aggiornamenti 2026-02-19
- Scheduler: mostrata ora server e prossimo start in UI.
- Versione add-on aggiornata a 0.6.85.


## Aggiornamenti 2026-02-19
- Fix: riparate funzioni scheduler e import datetime/ZoneInfo (crash avvio).
- Versione add-on aggiornata a 0.6.86.


## Aggiornamenti 2026-02-19
- Runtime: aggiunto timezone configurabile per scheduler (default Europe/Rome).
- Versione add-on aggiornata a 0.6.87.


## Aggiornamenti 2026-02-19
- UI: supporto hash `/#/user|admin|scheduler` per accesso diretto.
- Versione add-on aggiornata a 0.6.88.


## Aggiornamenti 2026-02-19
- UI: apertura tab da hash subito all'avvio (senza refresh).
- Versione add-on aggiornata a 0.6.90.


## Aggiornamenti 2026-02-19
- Gas emergenza: valvole PT/M+1P aprono solo con zone attive.
- Versione add-on aggiornata a 0.6.91.


## Aggiornamenti 2026-02-19
- Gas emergenza: PT attivo apre R2+R3; 1P/Mansarda da sole non aprono valvole.
- Versione add-on aggiornata a 0.6.92.


## Aggiornamenti 2026-02-19
- Gas emergenza: aggiunto R21 GAS MISC OFF (chiusa solo con gas attivo, altrimenti aperta).
- Versione add-on aggiornata a 0.6.93.


## Aggiornamenti 2026-02-19
- MQTT: configurazione in Admin + discovery (setpoint screenshot, moduli ON/OFF e stato attivo) con comandi R/W.
- Endpoint MQTT: `/api/mqtt/status`, `/api/mqtt/republish`, `/api/mqtt/clear`.
- UI: pulsanti Admin per ripubblica/reset MQTT.
- UI: header ridotto e allineato allo stile richiesto.
- Versione add-on aggiornata a 0.6.94.

## Aggiornamenti 2026-02-19
- MQTT: configurazione spostata in config dell’add-on (options.json); UI rimossa.
- Versione add-on aggiornata a 0.6.95.

## Aggiornamenti 2026-02-20
- Impianto: richiesta calore ora deriva dalle zone quando sono configurate (non dal sensore richiesta_heat).
- Versione add-on aggiornata a 0.6.96.

## Aggiornamenti 2026-02-20
- UI: Caldaia legna mostra stato startup (timer) e colore rosso solo quando attiva.
- Versione add-on aggiornata a 0.6.97.

## Aggiornamenti 2026-02-20
- Caldaia legna: reset startup ora riavvia il countdown (imposta deadline).
- Versione add-on aggiornata a 0.6.98.

## Aggiornamenti 2026-02-20
- UI: pulsante caldaia legna etichettato "Reset timer".
- Versione add-on aggiornata a 0.6.99.

## Aggiornamenti 2026-02-20
- Caldaia legna: se T mandata supera il minimo, lo startup timer si azzera subito.
- Versione add-on aggiornata a 0.7.0.

## Aggiornamenti 2026-02-20
- UI: caldaia legna mostra verde quando modulo ON ma inattivo (rosso solo se attivo).
- Versione add-on aggiornata a 0.7.1.

## Aggiornamenti 2026-02-20
- Resistenze: aggiunto input `extra_safe_w` e potenza disponibile `available_power_w` (usa il max tra export e safe).
- UI Admin: campo entitÃ  per `extra_safe_w` + storico.
- Versione add-on aggiornata a 0.7.2.


## Aggiornamenti 2026-02-20
- Fix: calcolo `available_w` nelle resistenze (evita errore NameError).
- Versione add-on aggiornata a 0.7.3.

## Aggiornamenti 2026-02-20
- Fix: definizione `available_w`/`extra_safe_w` in _apply_resistance_live.
- Versione add-on aggiornata a 0.7.4.

## Aggiornamenti 2026-02-20
- Fix build UI: rimosso codice JS finito nel blocco CSS di App.vue.
- Versione add-on aggiornata a 0.7.5.

## Aggiornamenti 2026-02-20
- Fix: fallback `available_w` sempre inizializzato in _apply_resistance_live.
- Versione add-on aggiornata a 0.7.6.

## Aggiornamenti 2026-02-20
- Resistenze: aggiunto input `extra_safe_total_w` e logica step con safe_possibile + export.
- Resistenze: step-down con delay anche in import.
- UI Admin: campo entità per `extra_safe_total_w`.
- Versione add-on aggiornata a 0.7.7.

## Aggiornamenti 2026-02-20
- Resistenze: limite step in base a `extra_safe_total_w` (cap totale).
- Versione add-on aggiornata a 0.7.8.

## Aggiornamenti 2026-02-20
- Resistenze: se export > totale, vince export (cap totale solo se export <= totale).
- Versione add-on aggiornata a 0.7.9.

## Aggiornamenti 2026-02-20
- Resistenze: blocco step quando batteria scarica (battery_output_w > 100W) con step-down delay.
- UI Admin: aggiunta entità `battery_output_w`.
- Versione add-on aggiornata a 0.7.10.

## Aggiornamenti 2026-02-20
- Resistenze: batteria scarica (battery_output_w > 100W) forza step=0 immediato.
- Versione add-on aggiornata a 0.7.11.

## Aggiornamenti 2026-02-20
- Resistenze: spegnimento immediato anche lato attuatori quando batteria scarica.
- Versione add-on aggiornata a 0.7.12.

## Aggiornamenti 2026-02-20
- Resistenze: step guidato da `extra_safe_w` (possibile), con cap su `extra_safe_total_w`.
- Versione add-on aggiornata a 0.7.13.

## Aggiornamenti 2026-02-20
- Fix avvio: spostato `global off_sequence_start` prima dell'uso.
- Versione add-on aggiornata a 0.7.14.

## Aggiornamenti 2026-02-20
- Resistenze: step guidato da produzione FV (`pv_power_w`).
- UI Admin: aggiunta entità `pv_power_w`.
- Versione add-on aggiornata a 0.7.15.

## Aggiornamenti 2026-02-20
- Resistenze: step guidato da `min(FV, total)`.
- Versione add-on aggiornata a 0.7.16.

## Aggiornamenti 2026-02-20
- Impianto: aggiunta opzione `auto_heat_keep_on` (default true) per non spegnere i termostati quando il modulo è inattivo.
- Versione add-on aggiornata a 0.7.17.

## Aggiornamenti 2026-02-20
- Impianto: termostati restano in HEAT solo quando non c'è domanda (no_demand). In caso di no_source vengono spenti.
- Versione add-on aggiornata a 0.7.18.

## Aggiornamenti 2026-02-20
- Impianto: evita flip-flop termostati; HEAT solo in no_demand, OFF in no_source.
- Versione add-on aggiornata a 0.7.19.

## Aggiornamenti 2026-02-20
- UI: aggiunte descrizioni sintetiche per la logica dei moduli.
- Versione add-on aggiornata a 0.7.20.

## Aggiornamenti 2026-02-20
- Resistenze: step da Possibile; se FV < Possibile usa Export. Export deve superare soglie.
- Versione add-on aggiornata a 0.7.21.

## Aggiornamenti 2026-02-20
- Resistenze: force OFF attuatori quando step=0 e export <= soglia.
- Versione add-on aggiornata a 0.7.22.

## Aggiornamenti 2026-02-20
- Resistenze: force OFF immediato quando export <= soglia (indipendente dallo step).
- Versione add-on aggiornata a 0.7.23.

## Aggiornamenti 2026-02-20
- Resistenze: safety all'avvio (force OFF attuatori dopo update/riavvio).
- Versione add-on aggiornata a 0.7.24.

## Aggiornamenti 2026-02-20
- Resistenze: step da Possibile solo se Export >= Possibile; altrimenti OFF.
- Versione add-on aggiornata a 0.7.25.

## Aggiornamenti 2026-02-20
- Resistenze: base power = Export se Export > Possibile, altrimenti Possibile. Export < -100W OFF secco.
- Batteria scarica: stop con step-down (no off immediato).
- Versione add-on aggiornata a 0.7.26.

## Aggiornamenti 2026-02-20
- Resistenze: se Possibile <= 0 allora step-down (non off immediato).
- Versione add-on aggiornata a 0.7.28.

## Aggiornamenti 2026-02-20
- Resistenze: forza OFF step superiori quando step scende.
- Versione add-on aggiornata a 0.7.29.

## Aggiornamenti 2026-02-20
- Resistenze: force OFF immediato quando batteria_out > soglia.
- Versione add-on aggiornata a 0.7.30.

## Aggiornamenti 2026-02-20
- Resistenze: debounce export_off con tempo step-down (evita on/off istantaneo).
- Versione add-on aggiornata a 0.7.31.

## Aggiornamenti 2026-02-20
- Resistenze: se Export>0 usa Export; se Export<=0 usa Possibile.
- Versione add-on aggiornata a 0.7.32.

## Aggiornamenti 2026-02-24
- Resistenze: usa Export solo se Export>Possibile; quando usa Export sottrae potenza resistenze.
- Versione add-on aggiornata a 0.7.33.

## Aggiornamenti 2026-02-24
- Resistenze: step-down sempre con delay (niente spegnimento immediato quando scende sotto soglia).
- Versione add-on aggiornata a 0.7.34.

## Aggiornamenti 2026-02-24
- Resistenze: se Export>Possibile, ignora Possibile per lo spegnimento (base Export prevale).
- Versione add-on aggiornata a 0.7.35.

## Aggiornamenti 2026-02-24
- Resistenze: memoria base Export se resistenze accese da Export (evita switch a Possibile durante cali temporanei).
- Versione add-on aggiornata a 0.7.36.

## Aggiornamenti 2026-02-24
- Resistenze: base Export usa Export+resistenze (ricostruisce export pre-accensione).
- Versione add-on aggiornata a 0.7.37.

## Aggiornamenti 2026-03-31
- Impianto: quando ACS usa Volano, impianto forza Puffer (se disponibile) altrimenti OFF.
- Debug UI: aggiunte soglie start/hold impianto (volano/puffer) con valori reali backend.
- Versione add-on aggiornata a 0.7.38.

## Aggiornamenti 2026-03-31
- Debug UI: aggiunte uscite impianto reali (R4/R5/R11/R12) nel pannello impianto.
- Versione add-on aggiornata a 0.7.39.

## Aggiornamenti 2026-04-01
- UI: aggiunta pagina "Admin Energy" per configurare le entità energia (export, extra safe, batteria, FV).
- Versione add-on aggiornata a 0.7.40.

## Aggiornamenti 2026-04-01
- Energy: curva manuale potenza carica batteria vs temperatura + calcolo Extra Safe interno.
- UI: aggiunti campi curva e sensori batteria (temp/SOC) in Admin Energy.
- Versione add-on aggiornata a 0.7.41.

## Aggiornamenti 2026-04-01
- Admin Energy: rimossi campi entità Extra Safe; mostrati valori calcolati in sola lettura.
- Versione add-on aggiornata a 0.7.42.

## Aggiornamenti 2026-04-01
- UI User: aggiunta sezione Energy con Extra Safe calcolati e temperatura batteria.
- Versione add-on aggiornata a 0.7.43.

## Aggiornamenti 2026-04-01
- Energy: doppio profilo EASAS/Privato con curve, entità e risultati separati.
- Admin Energy: aggiunti log ragionamento per EASAS/Privato.
- Versione add-on aggiornata a 0.7.44.

## Aggiornamenti 2026-04-01
- Energy: salvataggio curve accetta numeri con virgola e non resetta i valori.
- Versione add-on aggiornata a 0.7.45.

## Aggiornamenti 2026-04-01
- API: `/api/setpoints` ora include `energy_profiles` per persistenza curve.
- Versione add-on aggiornata a 0.7.46.

## Aggiornamenti 2026-04-01
- Energy: fix output JSON per profilo Privato (valori calcolati disponibili in UI).
- Versione add-on aggiornata a 0.7.47.

## Aggiornamenti 2026-04-21
- Cleanup backend: rimosso codice morto irraggiungibile in `backend/main.py` (nessun cambiamento funzionale).
- Testi modulo Impianto semplificati lato descrizione per spiegare meglio start/mantenimento senza termini troppo tecnici.
- Versione add-on aggiornata a 0.7.96.

## Aggiornamenti 2026-04-21 (UI spiegazioni semplici)
- Aggiunto nel tab User un pannello descrittivo "a prova di bambino" con stato e motivi numerici per ogni modulo principale.
- Posizionamento: subito sotto versione/stato, prima dei riquadri temperature.
- Versione add-on aggiornata a 0.7.97.

## Aggiornamenti 2026-04-21 (scarico volano fine giornata)
- Implementata logica di scarico VOLANO -> PUFFER a fine giornata per evitare perdita di calore quando ACS � prioritaria ma non prendibile.
- Parametri: `volano.evening_dump_enabled` (true) e `volano.evening_dump_after_h` (17.0).
- Versione add-on aggiornata a 0.7.98.

## Aggiornamenti 2026-04-21 (trigger dump + forzatura Volano->Puffer)
- Implementata scelta trigger automatico dump: `orario` o `entita HA RUN`.
- Aggiunta forzatura manuale temporizzata VOLANO->PUFFER via API e UI.
- Esposizione MQTT/HASS delle nuove entita di stato forzatura volano.
- Versione add-on aggiornata a 0.7.99.

## Aggiornamenti 2026-04-21 (entita RUN automatica)
- Aggiunta entita HA automatica `switch.thermomind_dump_volano_run` tramite MQTT discovery.
- Collegamento default al trigger dump `Entita RUN` per Volano->Puffer.
- Versione add-on aggiornata a 0.8.00.

- [2026-05-03] Branding addon: impostati logo.png e icon.png, versione 0.8.01.

- [2026-05-03] Release 0.8.02: pubblicato aggiornamento UI con logo in header.

- [2026-05-03] Release 0.8.03: splash screen iniziale Vue (3s) con fade e logo pubblico.

- [2026-05-03] Release 0.8.04: corretto path splash logo per compatibilit� ingress Home Assistant.

- [2026-05-03] Release 0.8.05: risolto TypeError reading 'acs' con default setpoints difensivi.

- [2026-05-03] Release 0.8.06: migliorata responsivit� smartphone e centratura splash screen.

- [2026-05-03] Release 0.8.07: risolto TypeError su sp.acs all'avvio e aggiunto favicon.

- [2026-05-03] Release 0.8.08: fix definitivo favicon.ico 404 con endpoint dedicato FastAPI.

- [2026-05-03] Release 0.8.09: evitato flood errori ERR_CONNECTION_REFUSED con gestione offline UI.

- [2026-05-20] Release 0.8.10: corretto blocco dump Volano->Puffer quando Volano->ACS e disabilitato; `source_to_acs` ora rispetta i moduli abilitati.

- [2026-05-20] Release 0.8.11: gating completo dei moduli OFF nelle decisioni, scarico volano non bloccato da VOL_MAX, e forzatura Volano->Puffer senza countdown se non applicabile.

- [2026-05-20] Release 0.8.12: dump automatico Volano->Puffer a VOL_MAX per creare headroom FV e priorita reale alla forzatura manuale scarico puffer.

- [2026-05-20] Release 0.8.13: Volano->Puffer autonomo con modulo ON quando ACS non usa il volano; ACS mantiene priorita se Volano->ACS e attivo e richiesto.

- [2026-05-20] Release 0.8.14: aggiunta pagina ALLARMI con layout operativo e allarmi chiari su blocchi ACS, puffer saturo, forzature, resistenze manuali e watchdog ACS da volano.

- [2026-05-20] Release 0.8.15: allarmi aggiuntivi per coerenza attuatori, R13, FV/resistenze, resa trasferimenti, configurazione e solare tutto chiuso; il modulo solare OFF mantiene una via aperta seguendo la modalita configurata.

- [2026-05-21] Release 0.8.16: aggiunto controllo Puffer MAX in UI/Admin e setpoint MQTT/HA per regolare la soglia puffer_max_hit.

- [2026-05-21] Release 0.8.17: corretto Volano->Puffer automatico, non richiede piu source_to_acs=OFF ma solo che source_to_acs non sia VOLANO.

- [2026-05-24] Release 0.8.18: i moduli OFF non forzano piu gli attuatori spenti, lasciando il comando manuale; solare OFF resta fail-safe su valvola notte/giorno.

- [2026-05-25] Release 0.8.19: solare fail-safe con watchdog backend permanente; R8/R9/R10 non possono restare tutte chiuse con modulo acceso/spento, reboot o aggiornamento. La modalita selezionata resta persistente; notte fissa e solo fallback di emergenza. Aggiunti allarmi backend di coerenza modalita/valvole.
- [2026-05-25] Release 0.8.20: pubblicati in MQTT/Home Assistant tutti gli allarmi della pagina ALLARMI nella sezione thermomind/alarms/..., con riepilogo e binary_sensor diagnostici per automazioni/notifiche.
- [2026-05-25] Release 0.8.21: aggiunto allarme `resistances_decision_mismatch` per disallineamento tra decisione modulo resistenze e stato fisico durante countdown spegnimento.
- [2026-05-25] Release 0.8.22: icona/pulsante ALLARMI nella card Stato quando ci sono allarmi attivi e log add-on con timestamp data+ora via configurazione Uvicorn.
- [2026-05-25] Release 0.8.23: corretta precedenza solare in modalita night; R10 puo attivarsi per SOLAR -> ACS, mentre R8 resta la via base fuori precedenza.
- [2026-05-25] Release 0.8.24: hotfix solare valvole sempre comandate da watchdog, anche con modulo acceso/spento e dopo reboot/update; allarme R10 ora segue la decisione SOLAR -> ACS.