# Worklog â€” e-ThermoMind

## 2026-02-08
- Normalizzazione config e setpoint con guardie su input e defaults.
- Aggiunte API `/api/entities` GET/POST e validazioni minime payload.
- Reconnect WS Home Assistant con backoff e logging base.
- UI Admin estesa per mapping entitÃ  HA.
- Fix encoding in titoli/UI e stringhe logica.
- Aggiornato `PROJECT_LOG.md` con stato e roadmap.
- Aggiunto `build.yaml` per forzare base image `base-python` nel build add-on.
- Avvio server tramite `uvicorn` nel Dockerfile (binding su 0.0.0.0:8099).
- Abilitati `homeassistant_api` e `hassio_api` per ottenere `SUPERVISOR_TOKEN`.
- Lettura fallback del token da `/run/secrets/supervisor_token`.
- Avvio in modalitÃ  standalone se il token Supervisor non Ã¨ disponibile.
- Serviti asset statici Vite da `/assets` per evitare pagina bianca.
- Endpoint debug `/api/assets` per verificare presenza file statici.
- Indicatore Online/Offline HA in UI (User/Admin) con endpoint `/api/status`.
- Supporto token HA da `options.json` con `ha_url`/`ha_token` (fallback se token Supervisor assente).
- Ricerca token Supervisor anche in `s6/container_environment` (compatibilitÃ  add-on).
- Mostrata versione add-on in User/Admin via `/api/status`.
- Versione UI ora letta da `config.yaml` (coerente con add-on).
- Polling UI automatico (refresh ogni 3s).
- Polling UI configurabile e timestamp ultimo aggiornamento in UI.
- Logica: isteresi ACS, hold VOLANO->ACS e stato last_* in decision.
- UI: configurazione attuatori + comandi manuali + stato attuatori.
- Logging con timestamp in output add-on.
- Etichette attuatori piu chiare (descrizione funzione).
- Etichetta pompa ACS specificata come PDC -> ACS.
- UI attuatori completa con canali R1-R30 (mapping manuale in Admin).
- Simbolo fisso per attuatori implementati (UI).
- Pallino verde/rosso per gestito/non gestito.
- Fix salvataggio attuatori (salva solo entity_id).
- Indicatore popolato/non popolato per entita e attuatori in Admin.
- Comandi manuali con toggle singolo e stato (icona da HA attributes).
- Toggle colorato per stato e icone MDI reali.
- MDI font locale bundlato via npm (icone HA visibili anche senza CDN).
- Icone toggle colorate per stato e aggiornamento attuatori via polling.
- Selettore runtime mode (dry-run/live) con conferma.
- LIVE resistenze volano con off-delay (R22/R23/R24).
- Log azioni e indicatori runtime mode in UI.
- Icone HA anche per i sensori (Admin + User).
- Admin: etichette e-manager, layout a sezioni, filtro attuatori, export/import config.
- Admin: pulsanti in header + setpoint compatti.
- User: mostra runtime mode e stato resistenze volano (R22/R23/R24).
- Import config anche in header.
- User: nomi completi resistenze + icone colorate per stato.
- Dry-run: log simulato step/export in "Ultime azioni".
- Compatibilita load sensori (stringa -> oggetto UI).
- Blocca refresh mentre si editano i campi (no sparizione input).
- Polling sospeso con focus globale input/select/textarea.
- Polling sospeso in tab Admin (no overwrite mentre si compila).
- Indicatore presenza: pallino rosso fisso + bordo verde se entity presente.
- Rimosso bordo verde; pallino rosso unico a sinistra.
- Indicatori ripristinati: verde = in logica, rosso = non in logica, bordo verde se entity presente.
- Bordo verde input piu evidente (2px + glow).
- Pallino logica spostato accanto all'input entita.
- Pallino logica accanto anche ai sensori.
- Toggle moduli anche in Admin (7 moduli).
- Dry-run: log simulato completo per moduli (stati ON/OFF/DISABLED) + flag volano->puffer.
- Moduli UI: evidenziazione ON con fondo rosso trasparente.
- PROJECT_LOG aggiornato con snapshot 2026-02-09.
- Rimossi comandi manuali, toggle via pallino attuatori + bordo rosso quando ON; user senza pallino.
- Header: pulsanti config uniformati e rimossa duplicazione in sezione Configurazione.
- Guard: se un attuatore ON da HA con modulo attivo, auto-OFF dopo 2s (UI toggle escluso).
- UI User: "Ultime azioni" in ordine inverso (nuove in cima).
- Input attuatori: bordo verde per entita presente + riempimento rosso quando ON.
- Forzato riempimento rosso input ON con !important.
- WebSocket UI: aggiornamento live per User/Admin senza sovrascrivere input in editing.
- Resistenze: aggiunti sensori potenza/energia + switch generale in logica (ON con step).
- Input mapping: blocco overwrite da WS quando campi sono "dirty" finchÃ© non salvi.
- WS: applica logica live resistenze durante snapshot (general OFF quando step=0).
- User: aggiunto R0 generale resistenze nella card Resistenze volano.
- User: schema impianto animato con flussi live.
- Resistenze: generale segue step (ON se step>0, OFF se step=0).
- Runtime mode: cambio live/dry-run salvato automaticamente.
## 2026-02-09
- UI: restyle completo e schema impianto piÃ¹ pulito e leggibile.
- Backend: attuazione live per Volanoâ†’ACS, Volanoâ†’Puffer e Pufferâ†’ACS con sequenze valvolaâ†’pompa.
- Config: aggiunti timer `valve_to_pump_start_s` e `valve_to_pump_stop_s` con campi UI.
- UI: sequenze separate Volanoâ†’ACS e Volanoâ†’Puffer con nomi logici.
- Config: timer separati per Volanoâ†’ACS e Volanoâ†’Puffer (start/stop).
- User: grafico rapido temperature + export.

## 2026-02-14
- Persistenza moduli: POST /api/modules ora salva modules_enabled su disco.
- Versione add-on aggiornata a 0.6.59.


## 2026-02-14
- Toggle moduli: UI invia solo chiave/valore e backend fa merge per evitare overwrite da payload vecchi.
- Versione add-on aggiornata a 0.6.61.


## 2026-02-14
- Setpoints: /api/setpoints non sovrascrive piu modules_enabled (restano gestiti da /api/modules, salvo blocco stagionale).
- Versione add-on aggiornata a 0.6.62.


## 2026-02-14
- Resistenze volano: se modulo OFF, non forza piu lo spegnimento (controllo manuale da HA).
- Versione add-on aggiornata a 0.6.63.


## 2026-02-18
- Watchdog impianto: logga stati incoerenti (no source/no demand con attuatori o zone ON), senza modificare la logica.
- Versione add-on aggiornata a 0.6.64.


## 2026-02-18
- Watchdog volano: logga se moduli transfer ON ma nessuna richiesta e attuatori restano ON.
- Versione add-on aggiornata a 0.6.65.


## 2026-02-18
- Impianto: isteresi separate ON/OFF per volano e puffer (salita/discesa).
- Watchdog aggiunti per resistenze, solare, miscelatrice, volano, gas, legna (solo log, nessuna azione).
- Versione add-on aggiornata a 0.6.66.


## 2026-02-18
- User: slider rapidi per setpoint Volano/Puffer/Impianto + select Stagione con salvataggio immediato.
- Versione add-on aggiornata a 0.6.67.


## 2026-02-18
- Solare: precedenza ACS attiva sempre quando T_SOL >= T_ACS+delta (fino ad ACS_MAX), indipendente da dest.
- Versione add-on aggiornata a 0.6.68.


## 2026-02-18
- User: slider ACS setpoint e ACS MAX con salvataggio immediato.
- Versione add-on aggiornata a 0.6.69.


## 2026-02-18
- UI User: sezione Watchdog con elenco filtrato (data + motivazione).
- Versione add-on aggiornata a 0.6.70.


## 2026-02-18
- UI User: badge lampeggiante ? ATTENZIONE: WATCHDOG se presenti eventi.
- Versione add-on aggiornata a 0.6.71.


## 2026-02-18
- UI User: pulsante Reset watchdog per azzerare la lista visibile.
- Versione add-on aggiornata a 0.6.72.


## 2026-02-18
- Impianto: log espliciti quando viene saltato per gas emergenza e quando spegne per no_source/no_demand.
- Versione add-on aggiornata a 0.6.73.


## 2026-02-18
- Zone active: ora contano solo hvac_action heating/cooling (idle non attivo).
- Versione add-on aggiornata a 0.6.74.


## 2026-02-18
- Zone active: off/idle non conta anche per gas emergenza (richiesta solo se state!=off e hvac_action=heating).
- Versione add-on aggiornata a 0.6.75.


## 2026-02-18
- Impianto: hold puffer/volano applicato con domanda anche senza last_source (evita stop a min+ON dopo restart).
- Versione add-on aggiornata a 0.6.76.


## 2026-02-18
- Impianto: inizializzazione di `demand_on` per evitare UnboundLocalError in `_apply_impianto_live`.
- Versione add-on aggiornata a 0.6.77.


## 2026-02-18
- Impianto: force OFF valvole/pompe quando inattivo (no_source/no_demand) e log motivi ON/OFF.
- Versione add-on aggiornata a 0.6.78.


## 2026-02-18
- Impianto: decisione UI allineata alla logica live (isteresi ON/OFF con domanda).
- Versione add-on aggiornata a 0.6.79.


## 2026-02-18
- Impianto: dopo GAS OFF riparte solo con isteresi ON (start_only finchÃ© la sorgente Ã¨ valida).
- Versione add-on aggiornata a 0.6.80.


## 2026-02-18
- UI: badge watchdog non lampeggia piÃ¹ per permettere la lettura.
- Versione add-on aggiornata a 0.6.81.


## 2026-02-19
- Log: de-dup azioni ripetute (stesso messaggio entro 5s aggiorna timestamp).
- Versione add-on aggiornata a 0.6.82.


## 2026-02-19
- Scheduler: pagina settimanale gas ON, timeline e persistenza.
- UI: header allineato allo stile richiesto.
- Versione add-on aggiornata a 0.6.83.


## 2026-02-19
- Fix: ripristinata funzione `_get_num` dopo inserimento scheduler (crash avvio).
- Versione add-on aggiornata a 0.6.84.


## 2026-02-19
- Scheduler: mostrata ora server e prossimo start in UI.
- Versione add-on aggiornata a 0.6.85.


## 2026-02-19
- Fix: riparate funzioni scheduler e import datetime/ZoneInfo (crash avvio).
- Versione add-on aggiornata a 0.6.86.


## 2026-02-19
- Runtime: aggiunto timezone configurabile per scheduler (default Europe/Rome).
- Versione add-on aggiornata a 0.6.87.


## 2026-02-19
- UI: supporto hash `/#/user|admin|scheduler` per accesso diretto.
- Versione add-on aggiornata a 0.6.88.


## 2026-02-19
- UI: apertura tab da hash subito all'avvio (senza refresh).
- Versione add-on aggiornata a 0.6.90.


## 2026-02-19
- Gas emergenza: valvole PT/M+1P aprono solo con zone attive.
- Versione add-on aggiornata a 0.6.91.


## 2026-02-19
- Gas emergenza: PT attivo apre R2+R3; 1P/Mansarda da sole non aprono valvole.
- Versione add-on aggiornata a 0.6.92.


## 2026-02-19
- Gas emergenza: aggiunto R21 GAS MISC OFF (chiusa solo con gas attivo, altrimenti aperta).
- Versione add-on aggiornata a 0.6.93.

## 2026-02-24
- Resistenze: usa Export solo se Export>Possibile; quando usa Export sottrae potenza resistenze.
- Versione add-on aggiornata a 0.7.33.

## 2026-02-24
- Resistenze: step-down sempre con delay (niente spegnimento immediato quando scende sotto soglia).
- Versione add-on aggiornata a 0.7.34.

## 2026-02-24
- Resistenze: se Export>Possibile, ignora Possibile per lo spegnimento (base Export prevale).
- Versione add-on aggiornata a 0.7.35.

## 2026-02-24
- Resistenze: memoria base Export se resistenze accese da Export (evita switch a Possibile durante cali temporanei).
- Versione add-on aggiornata a 0.7.36.

## 2026-02-24
- Resistenze: base Export usa Export+resistenze (ricostruisce export pre-accensione).
- Versione add-on aggiornata a 0.7.37.

## 2026-03-31
- Impianto: quando ACS usa Volano, impianto forza Puffer (se disponibile) altrimenti OFF.
- Debug UI: aggiunte soglie start/hold impianto (volano/puffer) con valori reali backend.
- Versione add-on aggiornata a 0.7.38.

## 2026-03-31
- Debug UI: aggiunte uscite impianto reali (R4/R5/R11/R12) nel pannello impianto.
- Versione add-on aggiornata a 0.7.39.

## 2026-04-01
- UI: aggiunta pagina "Admin Energy" per configurare le entitÃ  energia (export, extra safe, batteria, FV).
- Versione add-on aggiornata a 0.7.40.

## 2026-04-01
- Energy: curva manuale potenza carica batteria vs temperatura + calcolo Extra Safe interno.
- UI: aggiunti campi curva e sensori batteria (temp/SOC) in Admin Energy.
- Versione add-on aggiornata a 0.7.41.

## 2026-04-01
- Admin Energy: rimossi campi entitÃ  Extra Safe; mostrati valori calcolati in sola lettura.
- Versione add-on aggiornata a 0.7.42.

## 2026-04-01
- UI User: aggiunta sezione Energy con Extra Safe calcolati e temperatura batteria.
- Versione add-on aggiornata a 0.7.43.

## 2026-04-01
- Energy: doppio profilo EASAS/Privato con curve, entitÃ  e risultati separati.
- Admin Energy: aggiunti log ragionamento per EASAS/Privato.
- Versione add-on aggiornata a 0.7.44.

## 2026-04-01
- Energy: salvataggio curve accetta numeri con virgola e non resetta i valori.
- Versione add-on aggiornata a 0.7.45.

## 2026-04-01
- API: `/api/setpoints` ora include `energy_profiles` per persistenza curve.
- Versione add-on aggiornata a 0.7.46.

## 2026-04-01
- Energy: fix output JSON per profilo Privato (valori calcolati disponibili in UI).
- Versione add-on aggiornata a 0.7.47.


## 2026-04-01
- Energy: salvataggio curve/flag piu affidabile (debounce + reload setpoints in tab Energy).
- Energy: input curva salva anche la temperatura.
- Energy: batteria output ora usa il segno reale (negativo=carica).
- Versione add-on aggiornata a 0.7.48.

## 2026-04-01
- Energy UI: mostrati dettagli calcolo (max carica, carica attuale, headroom) per EASAS e Privato.
- Versione add-on aggiornata a 0.7.49.

## 2026-04-01
- Resistenze UI: mostrati export, extra safe, extra safe totale e disponibile calcolato.
- Versione add-on aggiornata a 0.7.50.

## 2026-04-01
- Runtime: default mode impostato a live per evitare ritorno in dry-run al riavvio.
- Versione add-on aggiornata a 0.7.51.

## 2026-04-01
- Resistenze: se gia ON, la base "possibile" somma la potenza resistenze per scalare step.
- Versione add-on aggiornata a 0.7.52.

## 2026-04-01
- Solare: default mode impostato a night (non auto).
- Versione add-on aggiornata a 0.7.53.

## 2026-04-01
- Runtime: aggiunto flag "forza LIVE al riavvio" (default ON).
- Solare: aggiunto flag "forza NOTTE al riavvio" (default ON).
- Versione add-on aggiornata a 0.7.54.

## 2026-04-01
- Solare: forza NOTTE applicata anche in runtime (valvole R8/R9) e salva mode al cambio UI.
- Versione add-on aggiornata a 0.7.55.

## 2026-04-01
- Energy curve: salvataggio solo a fine input (on change) per evitare autocorrezioni mentre scrivi.
- Versione add-on aggiornata a 0.7.56.

## 2026-04-01
- Energy curve: fix pulsanti aggiungi/rimuovi punti.
- Versione add-on aggiornata a 0.7.57.

## 2026-04-01
- Energy curve: disabilitato autosalvataggio sui campi per evitare riordino mentre scrivi; salva solo con pulsante.
- Versione add-on aggiornata a 0.7.58.

## 2026-04-01
- Energy curve: input T/W come testo (inputmode) per evitare salto di focus mentre scrivi.
- Versione add-on aggiornata a 0.7.59.

## 2026-04-01
- Energy: limite carica per SoC (>= soglia -> max W) configurabile per EASAS/Privato.
- Versione add-on aggiornata a 0.7.60.

## 2026-04-01
- Energy: default SoC limit 100% -> max charge 0W.
- Versione add-on aggiornata a 0.7.61.

## 2026-04-01
- Resistenze: se gia ON, la logica usa extra_safe + potenza resistenze per evitare spegnimenti immediati.
- Versione add-on aggiornata a 0.7.62.

## 2026-04-01
- UI: mostrata soglia spegnimento export (export_off_w) per resistenze.
- Versione add-on aggiornata a 0.7.63.

## 2026-04-01
- Energy: aggiunta curva SoC (es. 99%->500W, 100%->0W) per EASAS/Privato.
- Versione add-on aggiornata a 0.7.64.

## 2026-04-01
- Energy: log spiegazione estesa (temp, SoC, export, max carica, headroom, extra).
- Versione add-on aggiornata a 0.7.65.

## 2026-04-01
- Energy log: campo ragionamento multilinea con altezza variabile.
- Versione add-on aggiornata a 0.7.66.

## 2026-04-01
- Energy: aggiunto modulo riscaldatori batterie (EASAS/Privato) con logica PV+comfort e mapping attuatori.
- UI Energy: stato riscaldatori in User + configurazione in Admin.
- Energy log: formattazione multilinea pulita.
- Versione add-on aggiornata a 0.7.67.

## 2026-04-02
- Persistenza config: salvataggio atomico + backup e fallback su backup in caso di corruzione.
- Versione add-on aggiornata a 0.7.68.

## 2026-04-02
- Solare: aggiunta portata (L/min) e soglia minima per considerare il solare attivo.
- UI User: mostrata portata solare.
- UI Admin: campo entit? portata + soglia minima.
- Versione add-on aggiornata a 0.7.69.

## 2026-04-02
- Solare: fallback automatico su portata collettore se la portata solare dedicata non ? mappata.
- Versione add-on aggiornata a 0.7.70.

## 2026-04-02
- Impianto: logica richiesta basata su sorgenti valide (volano/puffer OK), non sulle zone.
- Tag IMPIANTO_LOGIC nel codice per evitare regressioni.
- Versione add-on aggiornata a 0.7.71.

## 2026-04-02
- UI Admin: aggiunta protezione per evitare reset liste zone durante modifica (manualEditHold).
- Versione add-on aggiornata a 0.7.72.

## 2026-04-02
- UI Admin: blocco salvataggio automatico history mentre si modificano le zone (evita sparizione immediata).
- Versione add-on aggiornata a 0.7.73.

## 2026-04-07
- Impianto: se nessuna zona attiva, spegne pompe/valvole pur mantenendo modulo attivo (zones_off).
- Versione add-on aggiornata a 0.7.74.

## 2026-04-07
- Solare: stop su ACS quando T_ACS >= setpoint (evita superare target).
- Versione add-on aggiornata a 0.7.75.

## 2026-04-09
- HA WS: retry/backoff in startup per evitare crash se Core non Ã¨ pronto.
- Versione add-on aggiornata a 0.7.76.

## 2026-04-09
- Resistenze: se modulo disabilitato, spegne una sola volta le resistenze (poi manuale libero).
- Versione add-on aggiornata a 0.7.77.

## 2026-04-11
- Impianto/Miscelatrice: fix domanda zone. Ora la richiesta impianto richiede sia sorgente valida sia domanda termostati/zone.
- Evitato caso di miscelatrice in regolazione continua (ALZA) quando non c'e domanda reale.
- Versione add-on aggiornata a 0.7.78.
## 2026-04-11
- Manifest add-on: sostituito arch deprecato rmv7 con rmhf.
- Versione add-on aggiornata a 0.7.79.
## 2026-04-11
- Config persistence: aggiunti log espliciti su load config (source=main|backup|default) con motivo fallback.
- Versione add-on aggiornata a 0.7.80.
## 2026-04-11
- Impianto: termostati in HEAT quando la fonte e' disponibile (anche senza richiesta zona immediata).
- Miscelatrice: resta inattiva se non c'e domanda zone, evitando regolazione continua a vuoto.
- Versione add-on aggiornata a 0.7.81.
## 2026-04-13
- ACS setpoint: alzato limite massimo da 65C a 85C (UI slider + MQTT number).
- Versione add-on aggiornata a 0.7.82.
## 2026-04-13
- Impianto: rimosso ritardo di riaccensione termostati (uto_heat_min_off_s) quando fonte disponibile.
- Con fonte OK i termostati tornano subito in HEAT; min_on resta attivo per anti-flap in spegnimento.
- Versione add-on aggiornata a 0.7.83.
## 2026-04-13
- UI Moduli: aggiunta riga esplicita stato ABILITATO/SPENTO e IN ESECUZIONE/NON IN ESECUZIONE.
- Versione add-on aggiornata a 0.7.84.
## 2026-04-13
- Impianto: isteresi hold corretta su sorgenti (PDC/Puffer) solo se la stessa sorgente era gia attiva; niente hold in avvio da fermo.
- Impianto: reset del latch sorgente quando source va OFF per evitare riagganci a soglia hold.
- Versione add-on aggiornata a 0.7.85.
## 2026-04-13
- UI moduli: Impianto ATTIVO ora richiede anche zone_demand (evita falsi "in esecuzione" con sole sorgenti disponibili).
- Backend: fissato bug latente in _set_climate_hvac_mode_guard (parametro eason definito).
- Versione add-on aggiornata a 0.7.86.
## 2026-04-13
- Forzatura emergenza ACS da puffer: nuova API temporizzata (`/api/acs/force_puffer` + clear) con scadenza automatica persistente.
- Logica ACS: se forzatura attiva e applicabile, selezione sorgente PUFFER senza modificare setpoint/config standard.
- Trasferimenti live: la pompa R14 può essere comandata dalla forzatura anche se modulo `puffer_to_acs` è OFF.
- UI User (Puffer -> ACS): aggiunti stato forzatura, durata timer e pulsanti avvio/stop forzatura.
- Pulizia: rimosso ramo morto `no_demand` in `_apply_impianto_live`.
- Build: frontend compilato con npm installato localmente; aggiunto `web/package-lock.json`.
- Versione add-on aggiornata a 0.7.87.
## 2026-04-13
- Fix salvataggio setpoint Solare: `flow_min_lmin` (portata minima start) ora viene persistito correttamente.
- Fix persistenza parametri Resistenze: aggiunti e salvati `export_off_w`, `battery_block_w`, `step_down_delay_s`.
- Fix persistenza parametri Impianto: ora vengono salvati anche `season_mode`, `auto_heat_min_on_s`, `auto_heat_min_off_s`, `auto_heat_keep_on`.
- UI fallback Solare: default locale allineato con `flow_min_lmin` per evitare valori undefined.
- Versione add-on aggiornata a 0.7.88.
## 2026-04-13
- Fix forzatura ACS da puffer: `STOP` non può più essere sovrascritto da salvataggi generici `/api/setpoints` (latch `force_acs_puffer_until_ts` protetto lato backend).
- UI: lock anti-doppio-click su pulsanti Forza/Stop forzatura (evita comandi concorrenti).
- Versione add-on aggiornata a 0.7.89.
## 2026-04-13
- MQTT discovery: corretto `unit_of_measurement` temperature da `Â°C` a `°C` (elimina lettera anomala nella UI HA).
- Versione add-on aggiornata a 0.7.90.
## 2026-04-13
- MQTT: aggiunta discovery + publish di sensori extra read-only (`thermomind/sensors/*`).
- Inclusi sensori logica principali: `dest`, `source_to_acs`, `acs_need`, `acs_ok`, `resistance_step`.
- Inclusi sensori impianto: `impianto_source`, `impianto_richiesta`, `impianto_zone_demand`, `impianto_blocked_cold`.
- Inclusi sensori forzatura: `force_acs_puffer_active`, `force_acs_puffer_remaining_s`.
- Inclusi sensori SAFE energia EASAS/Privato: extra safe, totale, headroom, max charge, export, battery output, temp, soc.
- Inclusi sensori temperature principali: `t_acs`, `t_puffer`, `t_volano`, `t_solare_mandata`, `t_esterna`, `solare_flow_lmin`.
- Versione add-on aggiornata a 0.7.91.
## 2026-04-17
- Resistenze Volano: fix regressione logica OFF. Ora la condizione di avvio/spegnimento usa la stessa base coerente con la regola (Export vs Possibile), evitando blocco con `Poss 0W` quando `Export` è valido.
- Resistenze Volano: resa robusta la valutazione `battery_block_w/export_off_w` anche fuori ramo attivo.
- Versione add-on aggiornata a 0.7.92.
## 2026-04-17
- Curva climatica: con `T esterna` non disponibile (`n/d`) il setpoint mandata ora va in fallback fisso a 45.0°C.
- Diagnostica modulo curva: aggiunto motivo esplicito `T_EXT n/d -> fallback SP 45.0C`.
- Versione add-on aggiornata a 0.7.93.
## 2026-04-19
- Diagnostica modulo: spiegazioni resa più chiara con `Decisione: Dest=... | Source=...` in tutte le reason principali (solare/volano/puffer/resistenze).
- Resistenze Volano: aggiunta diagnostica strutturata `stato/base/eff/step/blocchi` per capire subito perché resta OFF (es. VOL_MAX, Dest=OFF, Export soglia, potenza effettiva, batteria).
- Versione add-on aggiornata a 0.7.94.
## 2026-04-20
- Impianto: fix affidabilità spegnimento termostati quando `Source=OFF`.
- `_set_climate_hvac_mode`: corretto ordine controlli (`current state` prima del de-dup 30s) per evitare che un termostato tornato in HEAT venga lasciato acceso durante finestra di dedup.
- Valvole/pompe restano già forzate OFF nel ramo `no_source`.
- Versione add-on aggiornata a 0.7.95.
## 2026-04-21
- Cleanup backend: rimosso codice morto irraggiungibile in `main.py` dopo `return` (nessun impatto logico).
- Descrizione modulo Impianto resa più chiara e meno tecnica: esplicitato che parte sopra soglia avvio e resta attivo fino a soglia di mantenimento più bassa.
- Versione add-on aggiornata a 0.7.96.
## 2026-04-21
- UI User: aggiunto blocco "Cosa sta facendo adesso (spiegazione semplice)" sotto versione/stato e sopra le temperature.
- Spiegazione modulo-per-modulo con valori live (Solare, Volano->ACS, Puffer->ACS, Volano->Puffer, Resistenze, Impianto, Miscelatrice, Curva climatica).
- Versione add-on aggiornata a 0.7.97.
## 2026-04-21
- Volano -> Puffer: aggiunta regola fine giornata anti-spreco.
- Se dopo l'orario impostato (`volano.evening_dump_after_h`, default 17.0) ACS resta prioritaria ma non prendibile (`Dest=ACS` e `Source=OFF`), il volano scarica nel puffer quando le soglie minime sono rispettate.
- Nuovi parametri volano: `evening_dump_enabled` (default true) e `evening_dump_after_h`.
- Diagnostica estesa in reason `volano_to_puffer` con stato e motivo della regola fine giornata.
- Versione add-on aggiornata a 0.7.98.
## 2026-04-21
- Volano->Puffer: trigger dump configurabile (`volano.evening_dump_trigger`) con scelta `time` oppure `entity`.
- Nuovo campo `volano.evening_dump_run_entity` per usare un'entita HA RUN (on/off) come consenso automatico.
- Nuova forzatura manuale temporizzata VOLANO->PUFFER (`/api/volano/force_puffer` + clear), con timer dedicato in runtime.
- MQTT/HASS: aggiunte entita sensore `force_volano_puffer_active` e `force_volano_puffer_remaining_s`.
- UI User (card Volano->Puffer): aggiunti tasti "Scarica in Puffer"/"Stop scarico", durata e scelta trigger orario/entita.
- Versione add-on aggiornata a 0.7.99.
## 2026-04-21
- Creata entita RUN automatica via MQTT discovery: `switch.thermomind_dump_volano_run`.
- Trigger `Entita RUN` per dump Volano->Puffer ora usa di default `switch.thermomind_dump_volano_run`.
- MQTT: aggiunti topic command/state runtime `thermomind/runtime/volano_dump_run` e subscribe relativo.
- Versione add-on aggiornata a 0.8.00.

- [2026-05-03] Add-on: aggiunti logo.png/icon.png e bump versione a 0.8.01.

- [2026-05-03] Bump versione addon a 0.8.02 per rilascio aggiornamento UI logo.

- [2026-05-03] UI: aggiunto splash screen 3s con logo (/logo.png). Release 0.8.03.

- [2026-05-03] Fix splash logo su ingress HA: usato asset bundlato (:src=brandLogo). Release 0.8.04.

- [2026-05-03] Fix UI crash: fallback per sp.acs/sp.puffer null in load() (Vue). Release 0.8.05.

- [2026-05-03] UI mobile tuning + splash centrato (safe-area/dvh). Release 0.8.06.

- [2026-05-03] Fix mount crash UI (sp null/acs): default setpoints iniziali + favicon. Release 0.8.07.
