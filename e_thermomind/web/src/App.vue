<template>
  <div class="wrap">
    <header class="top">
      <div class="brand">e-ThermoMind</div>
      <div class="top-actions">
        <button class="action-btn" @click="saveAll">Salva tutto</button>
        <button class="action-btn" @click="exportConfig">Esporta config</button>
        <label class="action-btn upload">
          Importa config
          <input type="file" accept="application/json" @change="importConfig"/>
        </label>
      </div>
      <nav class="tabs">
        <button :class="{active: tab==='user'}" @click="tab='user'">User</button>
        <button :class="{active: tab==='admin'}" @click="tab='admin'">Admin</button>
      </nav>
    </header>

    <main class="main">
      <section v-if="tab==='user'" class="card">
        <h2>Stato (v0.2)</h2>
        <p class="muted">Dry-run: nessun comando agli attuatori. Serve per validare la logica.</p>

        <div v-if="d" class="grid">
          <div class="kpi" :class="historyEnabled('t_acs') ? 'clickable' : ''" @click="openHistory('t_acs','T_ACS')">
            <div class="k"><i v-if="mdiClass(ent?.t_acs?.attributes?.icon)" :class="mdiClass(ent?.t_acs?.attributes?.icon)"></i> T_ACS</div>
            <div class="v">{{ fmtTemp(d.inputs.t_acs) }}</div>
          </div>
          <div class="kpi" :class="historyEnabled('t_puffer') ? 'clickable' : ''" @click="openHistory('t_puffer','T_Puffer')">
            <div class="k"><i v-if="mdiClass(ent?.t_puffer?.attributes?.icon)" :class="mdiClass(ent?.t_puffer?.attributes?.icon)"></i> T_Puffer</div>
            <div class="v">{{ fmtTemp(d.inputs.t_puffer) }}</div>
          </div>
          <div class="kpi" :class="historyEnabled('t_volano') ? 'clickable' : ''" @click="openHistory('t_volano','T_Volano')">
            <div class="k"><i v-if="mdiClass(ent?.t_volano?.attributes?.icon)" :class="mdiClass(ent?.t_volano?.attributes?.icon)"></i> T_Volano</div>
            <div class="v">{{ fmtTemp(d.inputs.t_volano) }}</div>
          </div>
          <div class="kpi">
            <div class="k"><i v-if="mdiClass(ent?.grid_export_w?.attributes?.icon)" :class="mdiClass(ent?.grid_export_w?.attributes?.icon)"></i> Export rete</div>
            <div class="v">{{ fmtW(d.inputs.grid_export_w) }}</div>
          </div>
        </div>

        <div v-if="d" class="card inner">
          <div class="row"><strong>Grafico rapido (ultimi ~2-3 min)</strong></div>
          <div class="chart-grid">
            <div class="chart">
              <div class="chart-title">Temperature</div>
              <svg viewBox="0 0 300 90" role="img" aria-label="Grafico temperature">
                <polyline :points="sparkPoints(history.t_acs)" class="spark acs"/>
                <polyline :points="sparkPoints(history.t_puffer)" class="spark puffer"/>
                <polyline :points="sparkPoints(history.t_volano)" class="spark volano"/>
              </svg>
              <div class="axis-note">Y: {{ tempStats.label }}</div>
              <div class="axis-note">X: ultimi ~2–3 min</div>
              <div class="legend small">
                <span class="legend-item"><span class="legend-dot acs"></span> ACS</span>
                <span class="legend-item"><span class="legend-dot puffer"></span> Puffer</span>
                <span class="legend-item"><span class="legend-dot volano"></span> Volano</span>
              </div>
            </div>
            <div class="chart">
              <div class="chart-title">Export (W)</div>
              <svg viewBox="0 0 300 90" role="img" aria-label="Grafico export rete">
                <polyline :points="sparkPoints(history.export_w)" class="spark export"/>
              </svg>
              <div class="axis-note">Y: {{ exportStats.label }}</div>
              <div class="axis-note">X: ultimi ~2–3 min</div>
              <div class="legend small">
                <span class="legend-item"><span class="legend-dot export"></span> Export rete</span>
              </div>
            </div>
          </div>
        </div>

        <div class="statusline">
          <span class="muted">v{{ status?.version || '-' }}</span>
          <span class="muted">mode: {{ status?.runtime_mode || '-' }}</span>
          <span class="badge" :class="status?.ha_connected ? 'ok' : 'off'">
            {{ status?.ha_connected ? 'Online' : 'Offline' }}
          </span>
          <span class="muted">HA</span>
          <span class="muted">Ultimo aggiornamento: {{ lastUpdate ? lastUpdate.toLocaleTimeString() : '-' }}</span>
        </div>


        
        <div class="card inner">
          <div class="row"><strong>Moduli (User)</strong></div>
          <div class="row3">
            <button class="ghost toggle" :class="modules.resistenze_volano ? 'on' : 'off'" @click="toggleModule('resistenze_volano')">
              Resistenze Volano: {{ modules.resistenze_volano ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.volano_to_acs ? 'on' : 'off'" @click="toggleModule('volano_to_acs')">
              Volano → ACS: {{ modules.volano_to_acs ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.volano_to_puffer ? 'on' : 'off'" @click="toggleModule('volano_to_puffer')">
              Volano → Puffer: {{ modules.volano_to_puffer ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.puffer_to_acs ? 'on' : 'off'" @click="toggleModule('puffer_to_acs')">
              Puffer → ACS: {{ modules.puffer_to_acs ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.impianto ? 'on' : 'off'" @click="toggleModule('impianto')">
              Impianto Riscaldamento: {{ modules.impianto ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.solare ? 'on' : 'off'" @click="toggleModule('solare')">
              Solare: {{ modules.solare ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.miscelatrice ? 'on' : 'off'" @click="toggleModule('miscelatrice')">
              Miscelatrice: {{ modules.miscelatrice ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.pdc ? 'on' : 'off'" @click="toggleModule('pdc')">
              PDC: {{ modules.pdc ? 'ON' : 'OFF' }}
            </button>
          </div>
        </div>


        <div v-if="d" class="card inner">
          <div class="row"><strong>Destinazione surplus:</strong> {{ d.computed.dest }}</div>
          <div class="muted">{{ d.computed.dest_reason }}</div>
          <hr />
          <div class="row"><strong>Source -> ACS:</strong> {{ d.computed.source_to_acs }}</div>
          <div class="muted">{{ d.computed.source_reason }}</div>
          <hr />
          <div class="row"><strong>Carica riserva:</strong> {{ d.computed.charge_buffer }} (step {{ d.computed.resistance_step }}/3)</div>
          <div class="muted">{{ d.computed.charge_reason }}</div>
          <div v-if="moduleReasonsList.length">
            <hr />
            <div class="row"><strong>Moduli</strong></div>
            <div class="module-reasons">
              <div v-for="item in moduleReasonsList" :key="item.key" class="module-row">
                <div class="module-head">
                  <div class="module-label">{{ item.label }}</div>
                  <div class="module-badges">
                    <span class="badge-mini" :class="item.enabled ? 'on' : 'off'">
                      {{ item.enabled ? 'MOD ON' : 'MOD OFF' }}
                    </span>
                    <span class="badge-mini" :class="item.active ? 'active' : 'idle'">
                      {{ item.active ? 'ATTIVO' : 'INATTIVO' }}
                    </span>
                  </div>
                </div>
                <div class="muted">{{ item.reason }}</div>
              </div>
            </div>
          </div>
        </div>

        <div v-if="act" class="card inner">
          <div class="row"><strong>Resistenze volano</strong></div>
          <div class="row3">
            <div class="kpi kpi-center clickable" :class="stateClass(act?.r22_resistenza_1_volano_pdc?.state)" @click="userToggle(act?.r22_resistenza_1_volano_pdc, 'resistenze_volano')">
              <div class="k">
                <i v-if="mdiClass(act?.r22_resistenza_1_volano_pdc?.attributes?.icon)" :class="[mdiClass(act?.r22_resistenza_1_volano_pdc?.attributes?.icon), stateClass(act?.r22_resistenza_1_volano_pdc?.state)]"></i>
                R22 Resistenza 1 Volano PDC
              </div>
            </div>
            <div class="kpi kpi-center clickable" :class="stateClass(act?.r23_resistenza_2_volano_pdc?.state)" @click="userToggle(act?.r23_resistenza_2_volano_pdc, 'resistenze_volano')">
              <div class="k">
                <i v-if="mdiClass(act?.r23_resistenza_2_volano_pdc?.attributes?.icon)" :class="[mdiClass(act?.r23_resistenza_2_volano_pdc?.attributes?.icon), stateClass(act?.r23_resistenza_2_volano_pdc?.state)]"></i>
                R23 Resistenza 2 Volano PDC
              </div>
            </div>
            <div class="kpi kpi-center clickable" :class="stateClass(act?.r24_resistenza_3_volano_pdc?.state)" @click="userToggle(act?.r24_resistenza_3_volano_pdc, 'resistenze_volano')">
              <div class="k">
                <i v-if="mdiClass(act?.r24_resistenza_3_volano_pdc?.attributes?.icon)" :class="[mdiClass(act?.r24_resistenza_3_volano_pdc?.attributes?.icon), stateClass(act?.r24_resistenza_3_volano_pdc?.state)]"></i>
                R24 Resistenza 3 Volano PDC
              </div>
            </div>
            <div class="kpi kpi-center clickable" :class="stateClass(act?.generale_resistenze_volano_pdc?.state)" @click="userToggle(act?.generale_resistenze_volano_pdc, 'resistenze_volano')">
              <div class="k">
                <i :class="[mdiClass(act?.generale_resistenze_volano_pdc?.attributes?.icon) || 'mdi mdi-power', stateClass(act?.generale_resistenze_volano_pdc?.state)]"></i>
                R0 Generale Resistenze Volano PDC
              </div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">
                <i v-if="mdiClass(ent?.resistenze_volano_power?.attributes?.icon)" :class="mdiClass(ent?.resistenze_volano_power?.attributes?.icon)"></i>
                Potenza Resistenze
              </div>
              <div class="v">{{ fmtEntity(ent?.resistenze_volano_power) }}</div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">
                <i v-if="mdiClass(ent?.resistenze_volano_energy?.attributes?.icon)" :class="mdiClass(ent?.resistenze_volano_energy?.attributes?.icon)"></i>
                Energia Resistenze
              </div>
              <div class="v">{{ fmtEntity(ent?.resistenze_volano_energy) }}</div>
            </div>
          </div>
        </div>

        <div v-if="act" class="card inner">
          <div class="row"><strong>Volano → ACS</strong></div>
          <div class="row3">
            <div class="kpi kpi-center">
              <div class="k">
                <i v-if="mdiClass(ent?.t_volano?.attributes?.icon)" :class="mdiClass(ent?.t_volano?.attributes?.icon)"></i>
                T_Volano
              </div>
              <div class="v">{{ fmtTemp(d?.inputs?.t_volano) }}</div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">
                <i v-if="mdiClass(ent?.t_acs?.attributes?.icon)" :class="mdiClass(ent?.t_acs?.attributes?.icon)"></i>
                T_ACS
              </div>
              <div class="v">{{ fmtTemp(d?.inputs?.t_acs) }}</div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">Delta (Volano - ACS)</div>
              <div class="v">{{ fmtDelta(d?.inputs?.t_volano, d?.inputs?.t_acs) }}</div>
            </div>
          </div>
          <div class="row3">
            <div class="kpi kpi-center clickable" :class="stateClass(act?.r6_valve_pdc_to_integrazione_acs?.state)" @click="userToggle(act?.r6_valve_pdc_to_integrazione_acs, 'volano_to_acs')">
              <div class="k">
                <i v-if="mdiClass(act?.r6_valve_pdc_to_integrazione_acs?.attributes?.icon)" :class="[mdiClass(act?.r6_valve_pdc_to_integrazione_acs?.attributes?.icon), stateClass(act?.r6_valve_pdc_to_integrazione_acs?.state)]"></i>
                Valvola PDC → ACS
              </div>
            </div>
            <div class="kpi kpi-center clickable" :class="stateClass(act?.r13_pump_pdc_to_acs_puffer?.state)" @click="userToggle(act?.r13_pump_pdc_to_acs_puffer, 'volano_to_acs')">
              <div class="k">
                <i v-if="mdiClass(act?.r13_pump_pdc_to_acs_puffer?.attributes?.icon)" :class="[mdiClass(act?.r13_pump_pdc_to_acs_puffer?.attributes?.icon), stateClass(act?.r13_pump_pdc_to_acs_puffer?.state)]"></i>
                R13 Pompa PDC → ACS/Puffer
              </div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">Stato logica</div>
              <div class="v">{{ d?.computed?.flags?.volano_to_acs ? 'ATTIVO' : 'STOP' }}</div>
            </div>
          </div>
        </div>

        <div v-if="act" class="card inner">
          <div class="row"><strong>Volano → Puffer</strong></div>
          <div class="row3">
            <div class="kpi kpi-center">
              <div class="k">
                <i v-if="mdiClass(ent?.t_volano?.attributes?.icon)" :class="mdiClass(ent?.t_volano?.attributes?.icon)"></i>
                T_Volano
              </div>
              <div class="v">{{ fmtTemp(d?.inputs?.t_volano) }}</div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">
                <i v-if="mdiClass(ent?.t_puffer?.attributes?.icon)" :class="mdiClass(ent?.t_puffer?.attributes?.icon)"></i>
                T_Puffer
              </div>
              <div class="v">{{ fmtTemp(d?.inputs?.t_puffer) }}</div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">Delta (Volano - Puffer)</div>
              <div class="v">{{ fmtDelta(d?.inputs?.t_volano, d?.inputs?.t_puffer) }}</div>
            </div>
          </div>
          <div class="row3">
            <div class="kpi kpi-center clickable" :class="stateClass(act?.r7_valve_pdc_to_integrazione_puffer?.state)" @click="userToggle(act?.r7_valve_pdc_to_integrazione_puffer, 'volano_to_puffer')">
              <div class="k">
                <i v-if="mdiClass(act?.r7_valve_pdc_to_integrazione_puffer?.attributes?.icon)" :class="[mdiClass(act?.r7_valve_pdc_to_integrazione_puffer?.attributes?.icon), stateClass(act?.r7_valve_pdc_to_integrazione_puffer?.state)]"></i>
                R7 Valvola PDC → Puffer
              </div>
            </div>
            <div class="kpi kpi-center clickable" :class="stateClass(act?.r13_pump_pdc_to_acs_puffer?.state)" @click="userToggle(act?.r13_pump_pdc_to_acs_puffer, 'volano_to_puffer')">
              <div class="k">
                <i v-if="mdiClass(act?.r13_pump_pdc_to_acs_puffer?.attributes?.icon)" :class="[mdiClass(act?.r13_pump_pdc_to_acs_puffer?.attributes?.icon), stateClass(act?.r13_pump_pdc_to_acs_puffer?.state)]"></i>
                R13 Pompa PDC → ACS/Puffer
              </div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">Stato logica</div>
              <div class="v">{{ d?.computed?.flags?.volano_to_puffer ? 'ATTIVO' : 'STOP' }}</div>
            </div>
          </div>
        </div>

        <div v-if="act" class="card inner">
          <div class="row"><strong>Solare</strong></div>
          <div class="row3">
            <div class="kpi kpi-center" :class="historyEnabled('t_solare_mandata') ? 'clickable' : ''" @click="openHistory('t_solare_mandata','T_Solare mandata')">
              <div class="k">
                <i v-if="mdiClass(ent?.t_solare_mandata?.attributes?.icon)" :class="mdiClass(ent?.t_solare_mandata?.attributes?.icon)"></i>
                T_Solare mandata
              </div>
              <div class="v">{{ fmtTemp(d?.inputs?.t_solare_mandata) }}</div>
            </div>
            <div class="kpi kpi-center" :class="solarModeClass">
              <div class="k">Modalità</div>
              <div class="v">{{ sp?.solare?.mode || 'auto' }}</div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">Cutback</div>
              <div class="v">{{ d?.computed?.safety?.acs_max_hit ? 'ACS_MAX' : (d?.inputs?.t_solare_mandata >= (sp?.solare?.max_c || 90) ? 'SOL_MAX' : 'OK') }}</div>
            </div>
          </div>
          <div class="row3">
            <div class="kpi kpi-center" :class="stateClass(act?.r8_valve_solare_notte_low_temp?.state)">
              <div class="k">
                <i v-if="mdiClass(act?.r8_valve_solare_notte_low_temp?.attributes?.icon)" :class="[mdiClass(act?.r8_valve_solare_notte_low_temp?.attributes?.icon), stateClass(act?.r8_valve_solare_notte_low_temp?.state)]"></i>
                R8 Solare Notte/Low
              </div>
            </div>
            <div class="kpi kpi-center" :class="stateClass(act?.r9_valve_solare_normal_funz?.state)">
              <div class="k">
                <i v-if="mdiClass(act?.r9_valve_solare_normal_funz?.attributes?.icon)" :class="[mdiClass(act?.r9_valve_solare_normal_funz?.attributes?.icon), stateClass(act?.r9_valve_solare_normal_funz?.state)]"></i>
                R9 Solare Normal
              </div>
            </div>
            <div class="kpi kpi-center" :class="stateClass(act?.r10_valve_solare_precedenza_acs?.state)">
              <div class="k">
                <i v-if="mdiClass(act?.r10_valve_solare_precedenza_acs?.attributes?.icon)" :class="[mdiClass(act?.r10_valve_solare_precedenza_acs?.attributes?.icon), stateClass(act?.r10_valve_solare_precedenza_acs?.state)]"></i>
                R10 Precedenza ACS
              </div>
            </div>
          </div>
          <div class="row3">
            <div class="kpi kpi-center clickable" :class="stateClass(act?.r18_valve_ritorno_solare_basso?.state)" @click="userToggleManual(act?.r18_valve_ritorno_solare_basso)">
              <div class="k">
                <i v-if="mdiClass(act?.r18_valve_ritorno_solare_basso?.attributes?.icon)" :class="[mdiClass(act?.r18_valve_ritorno_solare_basso?.attributes?.icon), stateClass(act?.r18_valve_ritorno_solare_basso?.state)]"></i>
                R18 Ritorno Solare Basso
              </div>
            </div>
            <div class="kpi kpi-center clickable" :class="stateClass(act?.r19_valve_ritorno_solare_alto?.state)" @click="userToggleManual(act?.r19_valve_ritorno_solare_alto)">
              <div class="k">
                <i v-if="mdiClass(act?.r19_valve_ritorno_solare_alto?.attributes?.icon)" :class="[mdiClass(act?.r19_valve_ritorno_solare_alto?.attributes?.icon), stateClass(act?.r19_valve_ritorno_solare_alto?.state)]"></i>
                R19 Ritorno Solare Alto
              </div>
            </div>
          </div>
        </div>

        <div v-if="act" class="card inner">
          <div class="row"><strong>Puffer → ACS</strong></div>

<div class="card inner">
          <div class="row"><strong>Impianto riscaldamento (interno)</strong></div>
          <div class="row3">
            <div class="kpi kpi-center">
              <div class="k">Sorgente</div>
              <select v-model="sp.impianto.source_mode">
                <option value="AUTO">AUTO</option>
                <option value="PDC">PDC</option>
                <option value="VOLANO">VOLANO</option>
                <option value="CALDAIA">CALDAIA</option>
                <option value="PUFFER">PUFFER</option>
              </select>
            </div>
            <label class="kpi kpi-center checkbox">
              <input type="checkbox" v-model="sp.impianto.pdc_ready"/>
              <span>PDC ready</span>
            </label>
            <label class="kpi kpi-center checkbox">
              <input type="checkbox" v-model="sp.impianto.volano_ready"/>
              <span>Volano ready</span>
            </label>
            <label class="kpi kpi-center checkbox">
              <input type="checkbox" v-model="sp.impianto.caldaia_ready"/>
              <span>Caldaia ready</span>
            </label>
            <div class="kpi kpi-center">
              <div class="k">Richiesta calore</div>
              <div class="v">{{ d?.computed?.impianto?.richiesta ? 'ON' : 'OFF' }}</div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">Consenso miscelatrice</div>
              <div class="v">{{ d?.computed?.impianto?.miscelatrice ? 'ON' : 'OFF' }}</div>
            </div>
          </div>
          <div class="help">I checkbox sono manuali nel solo add-on. Richiesta calore e consenso miscelatrice sono in sola lettura.</div>
        </div>
          <div class="row3">
            <div class="kpi kpi-center">
              <div class="k">
                <i v-if="mdiClass(ent?.t_puffer?.attributes?.icon)" :class="mdiClass(ent?.t_puffer?.attributes?.icon)"></i>
                T_Puffer
              </div>
              <div class="v">{{ fmtTemp(d?.inputs?.t_puffer) }}</div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">
                <i v-if="mdiClass(ent?.t_acs?.attributes?.icon)" :class="mdiClass(ent?.t_acs?.attributes?.icon)"></i>
                T_ACS
              </div>
              <div class="v">{{ fmtTemp(d?.inputs?.t_acs) }}</div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">Delta (Puffer - ACS)</div>
              <div class="v">{{ fmtDelta(d?.inputs?.t_puffer, d?.inputs?.t_acs) }}</div>
            </div>
          </div>
          <div class="row3">
            <div class="kpi kpi-center clickable" :class="stateClass(act?.r14_pump_puffer_to_acs?.state)" @click="userToggle(act?.r14_pump_puffer_to_acs, 'puffer_to_acs')">
              <div class="k">
                <i v-if="mdiClass(act?.r14_pump_puffer_to_acs?.attributes?.icon)" :class="[mdiClass(act?.r14_pump_puffer_to_acs?.attributes?.icon), stateClass(act?.r14_pump_puffer_to_acs?.state)]"></i>
                R14 Pompa Puffer → ACS
              </div>
            </div>
            <div class="kpi kpi-center">
              <div class="k">Stato logica</div>
              <div class="v">{{ d?.computed?.flags?.puffer_to_acs ? 'ATTIVO' : 'STOP' }}</div>
            </div>
          </div>
        </div>

        <div v-if="d" class="card inner">
          <div class="row"><strong>Schema impianto (live)</strong></div>
          <div class="muted">Flussi evidenziati in tempo reale.</div>
          <div class="diagram diagram-photo" :style="{ backgroundImage: `url(${schemaImg})` }">
            <svg class="diagram-overlay" viewBox="0 0 1347 864" preserveAspectRatio="xMidYMid meet" role="img" aria-label="Schema impianto e-ThermoMind">
              <defs>
                <radialGradient id="dotGlow" cx="50%" cy="50%" r="50%">
                  <stop offset="0%" stop-color="#7ff6e6" stop-opacity="1"/>
                  <stop offset="100%" stop-color="#7ff6e6" stop-opacity="0"/>
                </radialGradient>
              </defs>

              <!-- Dots animati sui punti chiave (senza nuove linee sopra i componenti) -->
              <circle cx="1045" cy="205" r="10" class="pulse" :class="flowSolarToPuffer ? 'pulse-on' : ''"/>
              <circle cx="1180" cy="260" r="10" class="pulse" :class="flowSolarToAcs ? 'pulse-on' : ''"/>
              <circle cx="955" cy="360" r="10" class="pulse" :class="flowPufferToAcs ? 'pulse-on' : ''"/>
              <circle cx="835" cy="360" r="10" class="pulse" :class="flowPufferToImpianto ? 'pulse-on' : ''"/>
              <circle cx="380" cy="250" r="10" class="pulse" :class="flowPufferToLab ? 'pulse-on' : ''"/>
              <circle cx="850" cy="520" r="10" class="pulse" :class="flowVolanoToPuffer ? 'pulse-on' : ''"/>
              <circle cx="980" cy="520" r="10" class="pulse" :class="flowCaldaiaToPuffer ? 'pulse-on' : ''"/>
              <circle cx="900" cy="600" r="10" class="pulse" :class="flowVolanoToAcs ? 'pulse-on' : ''"/>
              <circle cx="300" cy="620" r="10" class="pulse" :class="flowPdcToVolano ? 'pulse-on' : ''"/>
              <circle cx="260" cy="470" r="10" class="pulse" :class="flowPdcToVolano ? 'pulse-on' : ''"/>
              <circle cx="250" cy="140" r="10" class="pulse" :class="flowVolanoToImpianto ? 'pulse-on' : ''"/>

              <!-- Linea animata: Volano -> ACS -->
              <path d="M420 650 H820 V520 H1140" class="tube" :class="flowVolanoToAcs ? 'tube-on' : ''"/>
            </svg>
          </div>
          <div class="legend">
            <span class="legend-item"><span class="legend-dot on"></span> Flusso attivo</span>
            <span class="legend-item"><span class="legend-dot"></span> Flusso inattivo</span>
          </div>
        </div>

        <div class="actions">
          <button @click="refresh">Aggiorna</button>
        </div>

        <div class="card inner">
          <div class="row"><strong>Ultime azioni</strong></div>
          <div v-if="actions.length === 0" class="muted">Nessuna azione registrata.</div>
          <div v-else>
            <div v-for="(line, idx) in actions.slice().reverse()" :key="`a-${idx}`" class="muted">{{ line }}</div>
          </div>
        </div>
      </section>

      <section v-else class="card">
        <h2>Admin (v0.2)</h2>
        <p class="muted">Setpoint interni e mapping e-manager.</p>
        <div class="statusline">
          <span class="muted">v{{ status?.version || '-' }}</span>
          <span class="muted">mode: {{ status?.runtime_mode || '-' }}</span>
          <span class="badge" :class="status?.ha_connected ? 'ok' : 'off'">
            {{ status?.ha_connected ? 'Online' : 'Offline' }}
          </span>
          <span class="muted">HA</span>
          <span class="muted">Ultimo aggiornamento: {{ lastUpdate ? lastUpdate.toLocaleTimeString() : '-' }}</span>
        </div>

        <div class="form">
          <h3 class="section">Configurazione</h3>
        </div>

        <div v-if="sp" class="form setpoint-grid">
          <h3 class="section">Setpoint</h3>
          <div class="set-section">
            <div class="section-title">Runtime</div>
            <div class="field">
              <label>Runtime mode</label>
              <select v-model="sp.runtime.mode" @change="confirmMode">
                <option value="dry-run">dry-run</option>
                <option value="live">live</option>
              </select>
            </div>
            <div class="field">
              <label>Polling UI (ms)</label>
              <input type="number" min="500" step="500" v-model.number="sp.runtime.ui_poll_ms"/>
            </div>
          </div>

          <div class="set-section">
            <div class="section-title">ACS</div>
            <div class="field"><label>ACS setpoint (C)</label><input type="number" step="0.5" v-model.number="sp.acs.setpoint_c"/></div>
            <div class="field"><label>ACS MAX (C)</label><input type="number" step="0.5" v-model.number="sp.acs.max_c"/></div>
          </div>

          <div class="set-section">
            <div class="section-title">Volano</div>
            <div class="field"><label>Volano margine (C)</label><input type="number" step="0.5" v-model.number="sp.volano.margin_c"/></div>
            <div class="field"><label>Volano MAX (C)</label><input type="number" step="0.5" v-model.number="sp.volano.max_c"/></div>
            <div class="field"><label>Δ Start Volano → ACS (C)</label><input type="number" step="0.5" v-model.number="sp.volano.delta_to_acs_start_c"/></div>
            <div class="field"><label>Δ Hold Volano → ACS (C)</label><input type="number" step="0.5" v-model.number="sp.volano.delta_to_acs_hold_c"/></div>
            <div class="field"><label>Δ Start Volano → Puffer (C)</label><input type="number" step="0.5" v-model.number="sp.volano.delta_to_puffer_start_c"/></div>
            <div class="field"><label>Δ Hold Volano → Puffer (C)</label><input type="number" step="0.5" v-model.number="sp.volano.delta_to_puffer_hold_c"/></div>
            <div class="field">
              <label>Sequenza Volano → ACS (valvola + pompa)</label>
              <div class="row2">
                <div class="mini-field">
                  <span class="mini-label">Start (s)</span>
                  <input type="number" step="1" v-model.number="sp.timers.volano_to_acs_start_s"/>
                </div>
                <div class="mini-field">
                  <span class="mini-label">Stop (s)</span>
                  <input type="number" step="1" v-model.number="sp.timers.volano_to_acs_stop_s"/>
                </div>
              </div>
              <div class="help">Prima apre la valvola, poi parte la pompa. In stop: valvola OFF, pompa OFF con ritardo.</div>
            </div>
            <div class="field">
              <label>Sequenza Volano → Puffer (valvola + pompa)</label>
              <div class="row2">
                <div class="mini-field">
                  <span class="mini-label">Start (s)</span>
                  <input type="number" step="1" v-model.number="sp.timers.volano_to_puffer_start_s"/>
                </div>
                <div class="mini-field">
                  <span class="mini-label">Stop (s)</span>
                  <input type="number" step="1" v-model.number="sp.timers.volano_to_puffer_stop_s"/>
                </div>
              </div>
              <div class="help">Valvola ON → ritardo → pompa ON. In stop: valvola OFF → ritardo → pompa OFF.</div>
            </div>
          </div>

          <div class="set-section">
            <div class="section-title">Puffer</div>
            <div class="field"><label>Puffer setpoint (C)</label><input type="number" step="0.5" v-model.number="sp.puffer.setpoint_c"/></div>
            <div class="field"><label>Δ Start Puffer → ACS (C)</label><input type="number" step="0.5" v-model.number="sp.puffer.delta_to_acs_start_c"/></div>
            <div class="field"><label>Δ Hold Puffer → ACS (C)</label><input type="number" step="0.5" v-model.number="sp.puffer.delta_to_acs_hold_c"/></div>
          </div>

          <div class="set-section">
            <div class="section-title">Resistenze</div>
            <div class="field"><label>Off-delay resistenze (s)</label><input type="number" step="1" v-model.number="sp.resistance.off_delay_s"/></div>
            <div class="field">
              <label>Soglie export (W) [1/2/3]</label>
              <div class="row3">
                <input type="number" v-model.number="sp.resistance.thresholds_w[0]"/>
                <input type="number" v-model.number="sp.resistance.thresholds_w[1]"/>
                <input type="number" v-model.number="sp.resistance.thresholds_w[2]"/>
              </div>
            </div>
          </div>

          <div class="set-section">
            <div class="section-title">Solare</div>
            <div class="field">
              <label>Modalità</label>
              <select v-model="sp.solare.mode">
                <option value="auto">auto (sun.sun)</option>
                <option value="night">notte fissa</option>
              </select>
            </div>
            <div class="field">
              <label>FV entity (W) per giorno/notte</label>
              <input type="text" v-model="sp.solare.pv_entity" placeholder="sensor.zcs_easas_1_activepower_pv_ext"/>
            </div>
            <div class="field"><label>Soglia giorno FV (W)</label><input type="number" step="10" v-model.number="sp.solare.pv_day_w"/></div>
            <div class="field"><label>Soglia notte FV (W)</label><input type="number" step="10" v-model.number="sp.solare.pv_night_w"/></div>
            <div class="field"><label>Debounce FV (s)</label><input type="number" step="10" v-model.number="sp.solare.pv_debounce_s"/></div>
            <div class="field"><label>Δ Start Solare → ACS (C)</label><input type="number" step="0.5" v-model.number="sp.solare.delta_on_c"/></div>
            <div class="field"><label>Δ Hold Solare → ACS (C)</label><input type="number" step="0.5" v-model.number="sp.solare.delta_hold_c"/></div>
            <div class="field"><label>Solare MAX (C)</label><input type="number" step="0.5" v-model.number="sp.solare.max_c"/></div>
            <div class="help">In NOTTE: R8 ON e R9 OFF. R18/R19 restano manuali con interblocco.</div>
          </div>

        </div>

        <div class="form">
          <h3 class="section">Moduli (Admin)</h3>
          <div class="row3">
            <button class="ghost toggle" :class="modules.resistenze_volano ? 'on' : 'off'" @click="toggleModule('resistenze_volano')">
              Resistenze Volano: {{ modules.resistenze_volano ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.volano_to_acs ? 'on' : 'off'" @click="toggleModule('volano_to_acs')">
              Volano → ACS: {{ modules.volano_to_acs ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.volano_to_puffer ? 'on' : 'off'" @click="toggleModule('volano_to_puffer')">
              Volano → Puffer: {{ modules.volano_to_puffer ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.puffer_to_acs ? 'on' : 'off'" @click="toggleModule('puffer_to_acs')">
              Puffer → ACS: {{ modules.puffer_to_acs ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.impianto ? 'on' : 'off'" @click="toggleModule('impianto')">
              Impianto Riscaldamento: {{ modules.impianto ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.solare ? 'on' : 'off'" @click="toggleModule('solare')">
              Solare: {{ modules.solare ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.miscelatrice ? 'on' : 'off'" @click="toggleModule('miscelatrice')">
              Miscelatrice: {{ modules.miscelatrice ? 'ON' : 'OFF' }}
            </button>
            <button class="ghost toggle" :class="modules.pdc ? 'on' : 'off'" @click="toggleModule('pdc')">
              PDC: {{ modules.pdc ? 'ON' : 'OFF' }}
            </button>
          </div>
        </div>

        <details class="form" open>
          <summary class="section">Sensori da e-manager</summary>
          <div class="field">
            <label>
              <i v-if="mdiClass(ent?.t_acs?.attributes?.icon)" :class="mdiClass(ent?.t_acs?.attributes?.icon)"></i>
              T_ACS
            </label>
            <div class="input-row">
              <span class="logic-dot" :class="isFilled(ent?.t_acs?.entity_id) ? 'logic-ok' : 'logic-no'">●</span>
                <input type="text"
                       :class="isFilled(ent?.t_acs?.entity_id) ? 'input-ok' : ''"
                       v-model="ent.t_acs.entity_id"
                       placeholder="sensor.acs_temp"
                       @input="dirtyEnt.t_acs = true"
                       @focus="onFocus" @blur="onBlur"/>
              <div class="history-inline"><label><input type="checkbox" v-model="sp.history.t_acs"/> Storico</label></div>
            </div>
          </div>
          <div class="field">
            <label>
              <i v-if="mdiClass(ent?.t_puffer?.attributes?.icon)" :class="mdiClass(ent?.t_puffer?.attributes?.icon)"></i>
              T_Puffer
            </label>
            <div class="input-row">
              <span class="logic-dot" :class="isFilled(ent?.t_puffer?.entity_id) ? 'logic-ok' : 'logic-no'">●</span>
                <input type="text"
                       :class="isFilled(ent?.t_puffer?.entity_id) ? 'input-ok' : ''"
                       v-model="ent.t_puffer.entity_id"
                       placeholder="sensor.puffer_temp"
                       @input="dirtyEnt.t_puffer = true"
                       @focus="onFocus" @blur="onBlur"/>
              <div class="history-inline"><label><input type="checkbox" v-model="sp.history.t_puffer"/> Storico</label></div>
            </div>
          </div>
          <div class="field">
            <label>
              <i v-if="mdiClass(ent?.t_volano?.attributes?.icon)" :class="mdiClass(ent?.t_volano?.attributes?.icon)"></i>
              T_Volano
            </label>
            <div class="input-row">
              <span class="logic-dot" :class="isFilled(ent?.t_volano?.entity_id) ? 'logic-ok' : 'logic-no'">●</span>
                <input type="text"
                       :class="isFilled(ent?.t_volano?.entity_id) ? 'input-ok' : ''"
                       v-model="ent.t_volano.entity_id"
                       placeholder="sensor.volano_temp"
                       @input="dirtyEnt.t_volano = true"
                       @focus="onFocus" @blur="onBlur"/>
              <div class="history-inline"><label><input type="checkbox" v-model="sp.history.t_volano"/> Storico</label></div>
            </div>
          </div>
          <div class="field">
            <label>
              <i v-if="mdiClass(ent?.t_solare_mandata?.attributes?.icon)" :class="mdiClass(ent?.t_solare_mandata?.attributes?.icon)"></i>
              T_Solare mandata
            </label>
            <div class="input-row">
              <span class="logic-dot" :class="isFilled(ent?.t_solare_mandata?.entity_id) ? 'logic-ok' : 'logic-no'">●</span>
                <input type="text"
                       :class="isFilled(ent?.t_solare_mandata?.entity_id) ? 'input-ok' : ''"
                       v-model="ent.t_solare_mandata.entity_id"
                       placeholder="sensor.solar_mandata"
                       @input="dirtyEnt.t_solare_mandata = true"
                       @focus="onFocus" @blur="onBlur"/>
              <div class="history-inline"><label><input type="checkbox" v-model="sp.history.t_solare_mandata"/> Storico</label></div>
            </div>
          </div>
            <div class="field">
              <label>
                <i v-if="mdiClass(ent?.grid_export_w?.attributes?.icon)" :class="mdiClass(ent?.grid_export_w?.attributes?.icon)"></i>
                Export rete (W)
              </label>
              <div class="input-row">
                <span class="logic-dot" :class="isFilled(ent?.grid_export_w?.entity_id) ? 'logic-ok' : 'logic-no'">●</span>
                <input type="text"
                       :class="isFilled(ent?.grid_export_w?.entity_id) ? 'input-ok' : ''"
                       v-model="ent.grid_export_w.entity_id"
                       placeholder="sensor.grid_export_w"
                       @input="dirtyEnt.grid_export_w = true"
                       @focus="onFocus" @blur="onBlur"/>
              </div>
            </div>
            <div class="field">
              <label>
                <i v-if="mdiClass(ent?.resistenze_volano_power?.attributes?.icon)" :class="mdiClass(ent?.resistenze_volano_power?.attributes?.icon)"></i>
                Potenza Resistenze Volano (W)
              </label>
              <div class="input-row">
                <span class="logic-dot" :class="isFilled(ent?.resistenze_volano_power?.entity_id) ? 'logic-ok' : 'logic-no'">●</span>
                <input type="text"
                       :class="isFilled(ent?.resistenze_volano_power?.entity_id) ? 'input-ok' : ''"
                       v-model="ent.resistenze_volano_power.entity_id"
                       placeholder="sensor.resistenze_volano_power"
                       @input="dirtyEnt.resistenze_volano_power = true"
                       @focus="onFocus" @blur="onBlur"/>
              </div>
            </div>
            <div class="field">
              <label>
                <i v-if="mdiClass(ent?.resistenze_volano_energy?.attributes?.icon)" :class="mdiClass(ent?.resistenze_volano_energy?.attributes?.icon)"></i>
                Energia Resistenze Volano
              </label>
              <div class="input-row">
                <span class="logic-dot" :class="isFilled(ent?.resistenze_volano_energy?.entity_id) ? 'logic-ok' : 'logic-no'">●</span>
                <input type="text"
                       :class="isFilled(ent?.resistenze_volano_energy?.entity_id) ? 'input-ok' : ''"
                       v-model="ent.resistenze_volano_energy.entity_id"
                       placeholder="sensor.resistenze_volano_energy"
                       @input="dirtyEnt.resistenze_volano_energy = true"
                       @focus="onFocus" @blur="onBlur"/>
              </div>
            </div>
          <div class="actions">
            <button class="ghost" @click="saveEntities">Salva sensori</button>
          </div>
        </details>

        <details class="form" open>
          <summary class="section">Attuatori da e-manager</summary>
          <div class="field">
            <label>Filtro</label>
            <input type="text" v-model="filterAct" placeholder="Cerca R22, PDC, solare..." @focus="onFocus" @blur="onBlur"/>
          </div>
          <div v-for="item in filteredActuators" :key="item.key" class="field">
            <label>
              {{ item.label }}
            </label>
            <div class="input-row">
              <button class="logic-dot dot-toggle" :class="item.impl ? 'logic-ok' : 'logic-no'" @click="toggleAct(item.key)" :title="`Toggle ${item.label}`">●</button>
              <input type="text"
                     :class="[isFilled(act?.[item.key]?.entity_id) ? 'input-ok' : '', act?.[item.key]?.state === 'on' ? 'input-on' : '']"
                     v-model="act[item.key].entity_id"
                     :placeholder="`switch.${item.key}`"
                     @input="dirtyAct[item.key] = true"
                     @focus="onFocus" @blur="onBlur"/>
            </div>
          </div>
          <div class="actions">
            <button class="ghost" @click="saveActuators">Salva attuatori</button>
          </div>
        </details>

        <div class="actions">
          <button class="ghost" @click="loadAll">Ricarica</button>
        </div>
      </section>
      <div v-if="historyModal.open" class="modal-backdrop" @click.self="closeHistory">
        <div class="modal">
          <div class="modal-head">
            <div class="modal-title">Storico 24h — {{ historyModal.title }}</div>
            <button class="ghost" @click="closeHistory">Chiudi</button>
          </div>
          <div class="modal-body">
            <svg viewBox="0 0 600 220" class="history-chart" role="img" aria-label="Grafico storico">
              <line :x1="historyModal.padL" :y1="historyModal.padT" :x2="historyModal.padL" :y2="historyModal.h - historyModal.padB" class="axis"/>
              <line :x1="historyModal.padL" :y1="historyModal.h - historyModal.padB" :x2="historyModal.w - historyModal.padR" :y2="historyModal.h - historyModal.padB" class="axis"/>
              <g v-for="t in historyModal.yTicks" :key="t.label">
                <line :x1="historyModal.padL - 4" :y1="t.y" :x2="historyModal.padL" :y2="t.y" class="axis"/>
                <text :x="historyModal.padL - 8" :y="t.y + 4" class="axis-label" text-anchor="end">{{ t.label }}</text>
              </g>
              <g v-for="t in historyModal.xTicks" :key="t.label">
                <line :x1="t.x" :y1="historyModal.h - historyModal.padB" :x2="t.x" :y2="historyModal.h - historyModal.padB + 4" class="axis"/>
                <text :x="t.x" :y="historyModal.h - historyModal.padB + 16" class="axis-label" text-anchor="middle">{{ t.label }}</text>
              </g>
              <polyline :points="historyModal.points" class="spark acs"/>
            </svg>
            <div class="legend small">
              <span class="legend-item"><span class="legend-dot acs"></span>{{ historyModal.title }}</span>
              <span class="legend-item muted">Y: °C ({{ historyModal.minY }}–{{ historyModal.maxY }})</span>
              <span class="legend-item muted">X: {{ historyModal.rangeLabel }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import schemaImg from './assets/centrale-termica.png'
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
const tab = ref('user')
const d = ref(null)
const sp = ref(null)
const ent = ref(null)
const act = ref(null)
const status = ref(null)
  let pollTimer = null
  let ws = null
const lastUpdate = ref(null)
const pollMs = ref(3000)
const actions = ref([])
const history = ref({
  t_acs: [],
  t_puffer: [],
  t_volano: [],
  export_w: []
})
const historyModal = ref({ open: false, title: '', points: '', minY: '-', maxY: '-', rangeLabel: '', xTicks: [], yTicks: [], w: 600, h: 220, padL: 40, padR: 10, padT: 10, padB: 20 })
const maxPoints = 60
  const filterAct = ref('')
  const editingCount = ref(0)
  const dirtyEnt = ref({})
  const dirtyAct = ref({})
let focusInHandler = null
let focusOutHandler = null
const modules = ref({
  resistenze_volano: true,
  volano_to_acs: false,
  volano_to_puffer: false,
  puffer_to_acs: false,
  impianto: false,
  solare: false,
  miscelatrice: false,
  pdc: false
})
const solareModeInit = ref(false)

const actuatorDefs = [
  { key: 'r1_valve_comparto_laboratorio', label: 'R1 Valvola Comparto Laboratorio (riscaldamento)', impl: false },
  { key: 'r2_valve_comparto_mandata_imp_pt', label: 'R2 Valvola Comparto Mandata Imp PT (riscaldamento)', impl: false },
  { key: 'r3_valve_comparto_mandata_imp_m1p', label: 'R3 Valvola Comparto Mandata Imp M+1P (riscaldamento)', impl: false },
  { key: 'r4_valve_impianto_da_puffer', label: 'R4 Valvola Impianto da Puffer', impl: false },
  { key: 'r5_valve_impianto_da_pdc', label: 'R5 Valvola Impianto da PDC', impl: false },
  { key: 'r31_valve_impianto_da_volano', label: 'R31 Valvola Impianto da Volano', impl: false },
  { key: 'r6_valve_pdc_to_integrazione_acs', label: 'R6 Valvola PDC -> Integrazione ACS', impl: true },
  { key: 'r7_valve_pdc_to_integrazione_puffer', label: 'R7 Valvola PDC -> Integrazione Puffer', impl: true },
  { key: 'r8_valve_solare_notte_low_temp', label: 'R8 Valvola Solare Notte/Low Temp', impl: true },
  { key: 'r9_valve_solare_normal_funz', label: 'R9 Valvola Solare Normal Funz', impl: true },
  { key: 'r10_valve_solare_precedenza_acs', label: 'R10 Valvola Solare Precedenza ACS', impl: true },
  { key: 'r11_pump_mandata_laboratorio', label: 'R11 Pompa Mandata Laboratorio', impl: false },
  { key: 'r12_pump_mandata_piani', label: 'R12 Pompa Mandata Piani', impl: false },
  { key: 'r13_pump_pdc_to_acs_puffer', label: 'R13 Pompa PDC -> ACS/Puffer', impl: true },
  { key: 'r14_pump_puffer_to_acs', label: 'R14 Pompa Puffer -> ACS', impl: true },
  { key: 'r15_pump_caldaia_legna', label: 'R15 Pompa Caldaia Legna -> Puffer', impl: false },
  { key: 'r16_cmd_miscelatrice_alza', label: 'R16 CMD Miscelatrice ALZA', impl: false },
  { key: 'r17_cmd_miscelatrice_abbassa', label: 'R17 CMD Miscelatrice ABBASSA', impl: false },
  { key: 'r18_valve_ritorno_solare_basso', label: 'R18 Valvola Ritorno Solare Basso', impl: true },
  { key: 'r19_valve_ritorno_solare_alto', label: 'R19 Valvola Ritorno Solare Alto', impl: true },
  { key: 'r20_ta_caldaia_legna', label: 'R20 TA Caldaia Legna', impl: false },
  { key: 'r21_libero', label: 'R21 Libero', impl: false },
  { key: 'r22_resistenza_1_volano_pdc', label: 'R22 Resistenza 1 Volano PDC', impl: true },
  { key: 'r23_resistenza_2_volano_pdc', label: 'R23 Resistenza 2 Volano PDC', impl: true },
  { key: 'r24_resistenza_3_volano_pdc', label: 'R24 Resistenza 3 Volano PDC', impl: true },
  { key: 'generale_resistenze_volano_pdc', label: 'R0 Generale Resistenze Volano PDC', impl: true },
  { key: 'r25_comparto_generale_pdc', label: 'R25 Comparto Generale PDC', impl: false },
  { key: 'r26_comparto_pdc1_avvio', label: 'R26 Comparto PDC 1 Avvio', impl: false },
  { key: 'r27_comparto_pdc2_avvio', label: 'R27 Comparto PDC 2 Avvio', impl: false },
  { key: 'r28_scarico_antigelo_mandata_pdc', label: 'R28 Scarico Antigelo Mandata PDC', impl: false },
  { key: 'r29_scarico_antigelo_ritorno_pdc', label: 'R29 Scarico Antigelo Ritorno PDC', impl: false },
  { key: 'r30_alimentazione_caldaia_legna', label: 'R30 Alimentazione Caldaia Legna', impl: false }
]

const isFilled = (v) => (typeof v === 'string' ? v.trim().length > 0 : false)
const filteredActuators = computed(() => {
  const q = filterAct.value.trim().toLowerCase()
  if (!q) return actuatorDefs
  return actuatorDefs.filter(a => (a.label.toLowerCase().includes(q) || a.key.toLowerCase().includes(q)))
})

const fmtTemp = (v) => (Number.isFinite(v) ? `${v.toFixed(1)}C` : 'n/d')
const fmtDelta = (a, b) => {
  const da = Number(a)
  const db = Number(b)
  if (!Number.isFinite(da) || !Number.isFinite(db)) return 'n/d'
  return `${(da - db).toFixed(1)}C`
}
const fmtW = (v) => (Number.isFinite(v) ? `${Math.round(v)} W` : 'n/d')
const fmtEntity = (e) => {
  if (!e) return 'n/d'
  const raw = e.state
  const unit = e.attributes?.unit_of_measurement || ''
  if (raw === null || raw === undefined) return 'n/d'
  const num = Number(raw)
  if (Number.isFinite(num)) return `${num} ${unit}`.trim()
  return `${raw} ${unit}`.trim()
}
function statsLabel(values, unit){
  if (!values || values.length === 0) return 'n/d'
  const min = Math.min(...values)
  const max = Math.max(...values)
  if (!Number.isFinite(min) || !Number.isFinite(max)) return 'n/d'
  return `${min.toFixed(1)}–${max.toFixed(1)} ${unit}`.trim()
}
const tempStats = computed(() => {
  const vals = []
  vals.push(...(history.value.t_acs || []))
  vals.push(...(history.value.t_puffer || []))
  vals.push(...(history.value.t_volano || []))
  return { label: statsLabel(vals, '°C') }
})
const exportStats = computed(() => {
  const vals = history.value.export_w || []
  if (!vals.length) return { label: 'n/d' }
  const min = Math.min(...vals)
  const max = Math.max(...vals)
  if (!Number.isFinite(min) || !Number.isFinite(max)) return { label: 'n/d' }
  return { label: `${Math.round(min)}–${Math.round(max)} W` }
})
const historyEnabled = (key) => !!sp.value?.history?.[key]
async function openHistory(key, title){
  if (!historyEnabled(key)) return
  const entId = ent.value?.[key]?.entity_id
  if (!entId) return
  const r = await fetch(`/api/history?entity_id=${encodeURIComponent(entId)}&hours=24`)
  if (!r.ok) return
  const data = await r.json()
  const items = Array.isArray(data?.items) ? data.items.flat() : []
  const points = []
  for (const st of items){
    const v = Number(st.state)
    if (!Number.isFinite(v)) continue
    const ts = new Date(st.last_changed || st.last_updated || st.last_reported || Date.now()).getTime()
    points.push([ts, v])
  }
  if (points.length === 0) return
  const step = Math.max(1, Math.floor(points.length / 200))
  const reduced = points.filter((_, i) => i % step === 0)
  const xs = reduced.map(p => p[0])
  const ys = reduced.map(p => p[1])
  const minX = Math.min(...xs)
  const maxX = Math.max(...xs)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)
  const spanX = Math.max(1, maxX - minX)
  const spanY = Math.max(0.1, maxY - minY)
  const w = 600
  const h = 220
  const padL = 40
  const padR = 10
  const padT = 10
  const padB = 20
  const innerW = w - padL - padR
  const innerH = h - padT - padB
  const pts = reduced.map(([x,y]) => {
    const px = padL + ((x - minX) / spanX) * innerW
    const py = h - padB - ((y - minY) / spanY) * innerH
    return `${px.toFixed(1)},${py.toFixed(1)}`
  }).join(' ')
  const fmtTime = (ts) => new Date(ts).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  const xTicks = [0, 0.25, 0.5, 0.75, 1].map(t => ({
    x: padL + t * innerW,
    label: fmtTime(minX + t * spanX)
  }))
  const yTicks = [0, 0.5, 1].map(t => ({
    y: h - padB - t * innerH,
    label: (minY + t * spanY).toFixed(1)
  }))
  const rangeLabel = `${new Date(minX).toLocaleDateString()} ${fmtTime(minX)} → ${fmtTime(maxX)}`
  historyModal.value = { open: true, title, points: pts, minY: minY.toFixed(1), maxY: maxY.toFixed(1), rangeLabel, xTicks, yTicks, w, h, padL, padR, padT, padB }
}
function closeHistory(){
  historyModal.value.open = false
}
const flowSolarToAcs = computed(() => d.value?.computed?.source_to_acs === 'SOLAR')
const flowVolanoToAcs = computed(() => d.value?.computed?.source_to_acs === 'VOLANO')
const flowPufferToAcs = computed(() => d.value?.computed?.source_to_acs === 'PUFFER')
const flowVolanoToPuffer = computed(() => d.value?.computed?.flags?.volano_to_puffer)
const flowPufferToVolano = computed(() => false)
const flowSolarToPuffer = computed(() => false)
const flowPufferToImpianto = computed(() => false)
const flowVolanoToImpianto = computed(() => false)
const flowPufferToLab = computed(() => false)
const flowMiscelatrice = computed(() => false)
const flowCaldaiaToPuffer = computed(() => false)
const moduleReasonsList = computed(() => {
  const mr = d.value?.computed?.module_reasons || {}
  const flags = d.value?.computed?.flags || {}
  const step = Number(d.value?.computed?.resistance_step || 0)
  const labels = [
    { key: 'solare', label: 'Solare', active: !!flags.solare_to_acs },
    { key: 'volano_to_acs', label: 'Volano -> ACS', active: !!flags.volano_to_acs },
    { key: 'volano_to_puffer', label: 'Volano -> Puffer', active: !!flags.volano_to_puffer },
    { key: 'puffer_to_acs', label: 'Puffer -> ACS', active: !!flags.puffer_to_acs },
    { key: 'impianto', label: 'Impianto Riscaldamento', active: false },
    { key: 'resistenze_volano', label: 'Resistenze Volano', active: step > 0 }
  ]
  return labels
    .filter(item => mr[item.key])
    .map(item => ({
      ...item,
      enabled: modules.value?.[item.key] !== false,
      reason: mr[item.key]
    }))
})

const solarModeClass = computed(() => {
  const mode = sp.value?.solare?.mode || 'auto'
  return mode === 'night' ? 'mode-night' : 'mode-day'
})
const flowChargeVolano = computed(() => (d.value?.computed?.resistance_step || 0) > 0)
const flowPdcToVolano = computed(() => false)

  function mergeEntities(next){
    if (!ent.value) { ent.value = next; return }
    for (const key of Object.keys(next || {})) {
      const prev = ent.value[key] || { entity_id: null }
      const keepId = (dirtyEnt.value?.[key] || editingCount.value > 0) ? prev.entity_id : next[key]?.entity_id
      ent.value[key] = { ...next[key], entity_id: keepId }
    }
  }
  function mergeActuators(next){
    if (!act.value) { act.value = next; return }
    for (const key of Object.keys(next || {})) {
      const prev = act.value[key] || { entity_id: null }
      const keepId = (dirtyAct.value?.[key] || editingCount.value > 0) ? prev.entity_id : next[key]?.entity_id
      act.value[key] = { ...next[key], entity_id: keepId }
    }
  }
async function refresh(){
  if (tab.value === 'admin' || editingCount.value > 0) return
  const r = await fetch('/api/decision'); d.value = await r.json()
  updateHistoryFromDecision(d.value)
  const s = await fetch('/api/status'); status.value = await s.json()
  const a = await fetch('/api/actions'); actions.value = (await a.json()).items || []
  await loadActuators()
  await load()
  lastUpdate.value = new Date()
}
async function loadModules(){
  const r = await fetch('/api/modules'); modules.value = await r.json()
}
async function load(){
  const r = await fetch('/api/setpoints'); sp.value = await r.json()
  if (!sp.value?.timers) {
    sp.value.timers = {
      volano_to_acs_start_s: 5,
      volano_to_acs_stop_s: 2,
      volano_to_puffer_start_s: 5,
      volano_to_puffer_stop_s: 2
    }
  }
  if (!sp.value?.history) {
    sp.value.history = { t_acs: false, t_puffer: false, t_volano: false, t_solare_mandata: false }
  }
  if (!sp.value?.solare) {
    sp.value.solare = { mode: 'auto', delta_on_c: 5, delta_hold_c: 2.5, max_c: 90, pv_entity: '', pv_day_w: 1000, pv_night_w: 300, pv_debounce_s: 300 }
  }
  if (!sp.value?.impianto) {
    sp.value.impianto = { source_mode: 'AUTO', pdc_ready: false, volano_ready: false, caldaia_ready: false, richiesta_heat: false }
  }
  if (sp.value?.runtime?.ui_poll_ms) {
    pollMs.value = Number(sp.value.runtime.ui_poll_ms) || 3000
  }
}
async function loadActuators(){
  if (editingCount.value > 0) return
  const r = await fetch('/api/actuators'); act.value = await r.json()
}
async function save(){
  await fetch('/api/setpoints',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(sp.value)})
  await refresh()
  if (sp.value?.runtime?.ui_poll_ms) {
    pollMs.value = Number(sp.value.runtime.ui_poll_ms) || 3000
    startPolling()
  }
}
async function saveAll(){
  await save()
  await saveEntities()
  await saveActuators()
}
async function toggleModule(key){
  const pin = sp.value?.security?.user_pin || ''
  let provided = ''
  if (pin) {
    provided = window.prompt('PIN') || ''
  }
  const next = { ...modules.value, [key]: !modules.value[key] }
  const res = await fetch('/api/modules',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({ modules: next, pin: provided })
  })
  if (!res.ok) return
  await loadModules()
}
async function confirmMode(){
  if (!sp.value?.runtime?.mode) return
  if (sp.value.runtime.mode === 'live') {
    const ok = window.confirm('Passare a LIVE? Questo abilita comandi reali agli attuatori.')
    if (!ok) sp.value.runtime.mode = 'dry-run'
  }
  await save()
}
async function loadEntities(){
  if (editingCount.value > 0) return
  const r = await fetch('/api/entities')
  const data = await r.json()
  const out = {}
  for (const key of Object.keys(data || {})) {
    const val = data[key]
    if (typeof val === 'string' || val === null) {
      out[key] = { entity_id: val || null, state: null, attributes: {}, icon: null }
    } else {
      out[key] = val
    }
  }
  ent.value = out
}
  async function saveEntities(){
    const payload = {}
    for (const key of Object.keys(ent.value || {})) {
      payload[key] = ent.value?.[key]?.entity_id || null
    }
    await fetch('/api/entities',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({entities: payload})})
    dirtyEnt.value = {}
    await refresh()
  }
  async function saveActuators(){
    const payload = {}
    for (const item of actuatorDefs) {
      payload[item.key] = act.value?.[item.key]?.entity_id || null
    }
    await fetch('/api/actuators',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({actuators: payload})})
    dirtyAct.value = {}
    await loadActuators()
  }
async function exportConfig(){
  const r = await fetch('/api/config')
  const data = await r.json()
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'thermomind_config.json'
  a.click()
  URL.revokeObjectURL(url)
}
async function importConfig(ev){
  const file = ev.target.files?.[0]
  if (!file) return
  const text = await file.text()
  let data = null
  try { data = JSON.parse(text) } catch { return }
  await fetch('/api/config',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)})
  await loadAll()
}
async function doAct(entity_id, action, opts = {}){
  if (!entity_id) return
  await fetch('/api/actuate',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({entity_id, action, manual: !!opts.manual})
  })
  await loadActuators()
}

function userToggle(entityObj, moduleKey){
  if (!entityObj?.entity_id) return
  if (status.value?.runtime_mode !== 'live') return
  if (moduleKey && !modules.value?.[moduleKey]) return
  const action = entityObj.state === 'on' ? 'off' : 'on'
  doAct(entityObj.entity_id, action)
}

function userToggleManual(entityObj){
  if (!entityObj?.entity_id) return
  const action = entityObj.state === 'on' ? 'off' : 'on'
  const ok = window.confirm(`Manuale solare: ${action.toUpperCase()} ${entityObj.entity_id}. Confermi?`)
  if (!ok) return
  doAct(entityObj.entity_id, action, { manual: true })
}
function stateLabel(state){
  if (state === 'on') return 'ON'
  if (state === 'off') return 'OFF'
  return state || '-'
}
function toggleAct(key){
  const ent = act.value?.[key]
  if (!ent?.entity_id) return
  const action = ent.state === 'on' ? 'off' : 'on'
  const label = actuatorDefs.find(a => a.key === key)?.label || ent.entity_id
  const ok = window.confirm(`Comando manuale su ${label} (${action.toUpperCase()}). Confermi?`)
  if (!ok) return
  doAct(ent.entity_id, action, { manual: true })
}
function mdiClass(icon){
  if (!icon || typeof icon !== 'string') return ''
  if (icon.startsWith('mdi:')) {
    const name = icon.slice(4)
    return `mdi mdi-${name}`
  }
  return ''
}
function stateClass(state){
  if (state === 'on') return 'state-on'
  if (state === 'off') return 'state-off'
  return 'state-unknown'
}
function connectWS(){
  if (ws) ws.close()
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  ws = new WebSocket(`${proto}://${location.host}/ws`)
  ws.onmessage = (ev) => {
    let payload = null
    try { payload = JSON.parse(ev.data) } catch { return }
    if (!payload) return
    d.value = payload.decision || d.value
    if (payload.decision) updateHistoryFromDecision(payload.decision)
    status.value = payload.status || status.value
    actions.value = payload.actions || actions.value
    modules.value = payload.modules || modules.value
    mergeEntities(payload.entities || {})
    mergeActuators(payload.actuators || {})
    lastUpdate.value = new Date()
  }
  ws.onclose = () => {
    setTimeout(connectWS, 2000)
  }
}

function pushHistory(arr, value){
  const v = Number(value)
  if (!Number.isFinite(v)) return
  arr.push(v)
  if (arr.length > maxPoints) arr.splice(0, arr.length - maxPoints)
}
function updateHistoryFromDecision(decision){
  if (!decision?.inputs) return
  pushHistory(history.value.t_acs, decision.inputs.t_acs)
  pushHistory(history.value.t_puffer, decision.inputs.t_puffer)
  pushHistory(history.value.t_volano, decision.inputs.t_volano)
  pushHistory(history.value.export_w, decision.inputs.grid_export_w)
}
function sparkPoints(values){
  const w = 300
  const h = 90
  const pad = 6
  if (!values || values.length < 2) return ''
  const min = Math.min(...values)
  const max = Math.max(...values)
  const span = max - min || 1
  return values.map((v, i) => {
    const x = pad + (i / (values.length - 1)) * (w - pad * 2)
    const y = h - pad - ((v - min) / span) * (h - pad * 2)
    return `${x.toFixed(1)},${y.toFixed(1)}`
  }).join(' ')
}
async function loadAll(){
  await load()
  await loadEntities()
  await loadActuators()
  await loadModules()
  await refresh()
}
function startPolling(){
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async()=>{
    await refresh()
  }, Math.max(500, pollMs.value))
}
function stopPolling(){
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = null
}
function onFocus(){
  editingCount.value += 1
  stopPolling()
}
function onBlur(){
  editingCount.value = Math.max(0, editingCount.value - 1)
  if (editingCount.value === 0) startPolling()
}
onMounted(async()=>{ 
  await loadAll(); 
  startPolling();
  connectWS();
  solareModeInit.value = true
  focusInHandler = (e) => {
    const tag = e.target?.tagName
    if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') onFocus()
  }
  focusOutHandler = (e) => {
    const tag = e.target?.tagName
    if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') onBlur()
  }
  window.addEventListener('focusin', focusInHandler)
  window.addEventListener('focusout', focusOutHandler)
})
onBeforeUnmount(()=>{ 
  stopPolling();
  if (ws) ws.close()
  if (focusInHandler) window.removeEventListener('focusin', focusInHandler)
  if (focusOutHandler) window.removeEventListener('focusout', focusOutHandler)
})
watch(tab, (val) => {
  if (val === 'admin') {
    stopPolling()
  } else {
    startPolling()
  }
})

watch(
  () => sp.value?.solare?.mode,
  async (val, old) => {
    if (!solareModeInit.value) return
    if (val === undefined || val === old) return
    await save()
  }
)
</script>

<style>
:root{--bg:#070a0f;--card:#0b101a;--muted:#9fb0c7;--text:#e8f1ff;--accent:#57e3d6;--accent-2:#7aa7ff;--border:rgba(255,255,255,.08)}
*{box-sizing:border-box} body{margin:0;font-family:"Space Grotesk","IBM Plex Sans","Trebuchet MS",sans-serif;background:radial-gradient(1200px 500px at 20% -10%, rgba(122,167,255,.08), transparent),radial-gradient(900px 500px at 80% 0%, rgba(87,227,214,.06), transparent),var(--bg);color:var(--text)}
.wrap{min-height:100vh;display:flex;flex-direction:column}
.top{display:flex;align-items:center;justify-content:space-between;padding:16px 18px;border-bottom:1px solid var(--border);position:sticky;top:0;background:rgba(10,15,22,.85);backdrop-filter:blur(14px)}
.brand{font-weight:800;letter-spacing:.3px}
.tabs button{background:transparent;color:var(--text);border:1px solid var(--border);padding:8px 12px;border-radius:12px;margin-left:8px;cursor:pointer}
.tabs button.active{border-color:var(--accent);color:var(--accent)}
.main{padding:18px;max-width:1100px;margin:0 auto;width:100%}
.card{background:linear-gradient(180deg, rgba(11,16,26,.98), rgba(9,14,22,.98));border:1px solid var(--border);border-radius:20px;padding:18px;box-shadow:0 18px 40px rgba(0,0,0,.38)}
.card.inner{margin-top:14px}
.muted{color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:10px}
@media(min-width:760px){.grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
.kpi{border:1px solid var(--border);border-radius:14px;padding:10px;background:rgba(10,15,22,.6)}
.kpi.kpi-center{display:flex;flex-direction:column;justify-content:center;align-items:center;text-align:center;min-height:72px}
.kpi.kpi-center .k{display:flex;align-items:center;gap:6px;justify-content:center}
.checkbox{gap:8px}
.checkbox input{accent-color:#57e3d6}
.kpi.clickable{cursor:pointer;transition:transform .15s ease, box-shadow .15s ease}
.kpi.clickable:hover{transform:translateY(-1px);box-shadow:0 6px 18px rgba(0,0,0,.25)}
.mode-night{border-color:rgba(59,130,246,.6);background:rgba(59,130,246,.12);box-shadow:0 0 0 1px rgba(59,130,246,.2) inset, 0 0 18px rgba(59,130,246,.25)}
.mode-day{border-color:rgba(250,204,21,.6);background:rgba(250,204,21,.10);box-shadow:0 0 0 1px rgba(250,204,21,.2) inset, 0 0 18px rgba(250,204,21,.25)}
.k{font-size:12px;color:var(--muted)} .v{font-size:18px;font-weight:700;margin-top:2px}
.actions{margin-top:14px;display:flex;gap:10px;flex-wrap:wrap}
button{background:linear-gradient(135deg, var(--accent), #6cf1c9);border:none;color:#062524;padding:10px 12px;border-radius:14px;font-weight:700;cursor:pointer}
button.ghost{background:transparent;border:1px solid var(--border);color:var(--text)}
hr{border:0;border-top:1px solid var(--border);margin:12px 0}
.form{display:grid;gap:10px;margin-top:10px}
.section{margin:6px 0 2px 0;font-size:14px;color:var(--text)}
.field label{display:block;font-size:12px;color:var(--muted);margin-bottom:6px}
.help{font-size:11px;color:var(--muted);margin-top:6px;line-height:1.3}
.field select{width:100%;padding:10px;border-radius:12px;border:1px solid var(--border);background:#0e1522;color:var(--text)}
.field input{width:100%;padding:10px;border-radius:12px;border:1px solid var(--border);background:#0e1522;color:var(--text)}
.upload{display:inline-flex;align-items:center;gap:8px}
.upload input{display:none}
details.form{border:1px solid var(--border);border-radius:14px;padding:10px;background:rgba(0,0,0,.08)}
details.form summary{cursor:pointer;list-style:none}
.top-actions{display:flex;gap:8px;align-items:center}
.action-btn{background:linear-gradient(135deg, var(--accent), #6cf1c9);border:none;color:#062524;padding:10px 12px;border-radius:14px;font-weight:700;cursor:pointer}
.action-btn.upload{display:inline-flex;align-items:center;gap:6px}
.setpoint-grid{display:grid;gap:10px}
.setpoint-grid .section{grid-column:1/-1}
@media(min-width:900px){.setpoint-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.set-section{border:1px solid var(--border);border-radius:14px;padding:12px;background:rgba(10,15,22,.45)}
.set-section .section-title{font-size:12px;letter-spacing:.6px;text-transform:uppercase;color:var(--muted);margin-bottom:8px}
.row3{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.row3 input::placeholder{color:rgba(159,176,199,.6)}
.row2{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
.mini-field{display:flex;flex-direction:column;gap:6px}
.mini-label{font-size:11px;color:var(--muted)}
.chart-grid{display:grid;gap:12px}
@media(min-width:900px){.chart-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.chart{border:1px solid var(--border);border-radius:14px;padding:10px;background:rgba(10,15,22,.6)}
.chart-title{font-size:12px;color:var(--muted);margin-bottom:6px}
.axis-note{font-size:10px;color:var(--muted);margin-top:4px}
.spark{fill:none;stroke-width:2}
.spark.acs{stroke:#57e3d6}
.spark.puffer{stroke:#7aa7ff}
.spark.volano{stroke:#f59e0b}
.spark.export{stroke:#ef4444}
.legend.small{margin-top:6px;gap:10px}
.legend-dot.acs{background:#57e3d6}
.legend-dot.puffer{background:#7aa7ff}
.legend-dot.volano{background:#f59e0b}
.legend-dot.export{background:#ef4444}
.statusline{display:flex;align-items:center;gap:8px;margin:8px 0 12px 0;flex-wrap:wrap}
.badge{font-size:12px;padding:4px 8px;border-radius:999px;border:1px solid var(--border)}
.badge.ok{color:#0b1f1c;background:var(--accent)}
.badge.off{color:#f5f7fa;background:#3b3f46}
.presence{display:inline-block;margin-right:6px}
.presence-ok{color:#22c55e}
.presence-no{color:#ef4444}
.input-ok{border:2px solid #22c55e; box-shadow:0 0 0 2px rgba(34,197,94,0.15)}
.input-row{display:flex;align-items:center;gap:8px}
.history-inline{display:flex;align-items:center;gap:6px;margin-left:10px;font-size:11px;color:var(--muted)}
.logic-dot{display:inline-block}
.logic-ok{color:#22c55e}
.logic-no{color:#ef4444}
.toggle{justify-content:flex-start;gap:8px}
.toggle.on{border-color:rgba(239,68,68,.45);background:linear-gradient(135deg, rgba(239,68,68,.22), rgba(239,68,68,.08));box-shadow:0 0 0 1px rgba(239,68,68,.08) inset}
.toggle.off{border-color:var(--border);background:transparent}
.mdi-fallback{font-size:14px;opacity:0.8}
.state-on{color:#ef4444}
.state-off{color:#94a3b8}
.state-unknown{color:#f59e0b}
.kpi.state-on{border-color:rgba(239,68,68,.45);background:rgba(239,68,68,.08)}
.kpi.state-off{border-color:var(--border)}
.input-on{background:rgba(239,68,68,.12) !important}
.dot-toggle{border:0;background:transparent;cursor:pointer;padding:0 2px}
.diagram{margin-top:10px;border:1px solid var(--border);border-radius:16px;padding:16px;background:
  radial-gradient(900px 320px at 70% 10%, rgba(87,227,214,.08), transparent),
  radial-gradient(800px 300px at 20% 90%, rgba(122,167,255,.08), transparent),
  repeating-linear-gradient(135deg, rgba(255,255,255,.01), rgba(255,255,255,.01) 12px, transparent 12px, transparent 24px),
  linear-gradient(180deg, rgba(6,10,16,.85), rgba(6,10,16,.55));
  box-shadow: inset 0 0 50px rgba(0,0,0,.55)}
.diagram-photo{
  padding:0;
  aspect-ratio:1347/864;
  min-height:360px;
  background-position:center center;
  background-repeat:no-repeat;
  background-size:contain;
  position:relative;
}
.diagram-overlay{
  width:100%;
  height:100%;
  display:block;
  position:absolute;
  inset:0;
  pointer-events:none;
}
.pulse{
  fill:url(#dotGlow);
  opacity:0;
}
.pulse-on{
  opacity:1;
  animation:pulse 1.6s ease-in-out infinite;
}
.tube{
  fill:none;
  stroke:rgba(87,227,214,.3);
  stroke-width:7;
  stroke-linecap:round;
}
.tube-on{
  stroke:url(#flowGrad);
  stroke-dasharray:18 10;
  animation:tubeFlow 1.4s linear infinite;
  filter:drop-shadow(0 0 6px rgba(87,227,214,.6));
}
@keyframes pulse{
  0%{r:6;opacity:.4}
  50%{r:12;opacity:1}
  100%{r:6;opacity:.4}
}
@keyframes tubeFlow{
  0%{stroke-dashoffset:0}
  100%{stroke-dashoffset:-56}
}
.diagram svg{width:100%;height:auto}
.node{fill:url(#nodeGrad);stroke:rgba(255,255,255,.08);filter:drop-shadow(0 6px 18px rgba(0,0,0,.35))}
.node-active{stroke:rgba(87,227,214,.75);filter:drop-shadow(0 0 12px rgba(87,227,214,.55))}
.node-label{fill:#e6edf3;font-size:13px;font-weight:700}
.node-sub{fill:#9aa4b2;font-size:11px}
.flow-line{stroke:#2b3447;stroke-width:5.5;fill:none;stroke-linecap:round}
.flow-line.dashed{stroke-dasharray:10 8;opacity:.6}
.flow-on{stroke:url(#flowGrad);filter:drop-shadow(0 0 6px rgba(87,227,214,.45));animation:flow 1.6s linear infinite}
.dot{fill:#2b3447}
.dot-on{fill:#57e3d6;filter:drop-shadow(0 0 6px rgba(87,227,214,.55))}
.legend{display:flex;gap:14px;margin-top:8px;flex-wrap:wrap}
.legend-item{display:flex;align-items:center;gap:6px;color:var(--muted);font-size:12px}
.legend-dot{width:10px;height:10px;border-radius:999px;background:#2b3447}
.legend-dot.on{background:#4fd1c5}
.modal-backdrop{position:fixed;inset:0;background:rgba(0,0,0,.6);display:flex;align-items:center;justify-content:center;z-index:50}
.modal{background:linear-gradient(180deg, rgba(11,16,26,.98), rgba(9,14,22,.98));border:1px solid var(--border);border-radius:16px;max-width:760px;width:90%;padding:14px;box-shadow:0 20px 50px rgba(0,0,0,.5)}
.modal-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:8px}
.modal-title{font-weight:700}
.axis{stroke:#2b3447;stroke-width:1}
.axis-label{fill:#9fb0c7;font-size:10px}
.history-chart{width:100%;height:auto}
.module-reasons{display:grid;gap:8px;margin-top:6px}
.module-row{border:1px solid var(--border);border-radius:12px;padding:8px 10px;background:rgba(10,15,22,.45)}
.module-head{display:flex;align-items:center;justify-content:space-between;gap:10px}
.module-label{font-size:12px;font-weight:700;letter-spacing:.3px}
.module-badges{display:flex;gap:6px;align-items:center}
.badge-mini{font-size:10px;border:1px solid var(--border);padding:2px 6px;border-radius:999px;color:var(--muted)}
.badge-mini.on{background:rgba(87,227,214,.12);border-color:rgba(87,227,214,.4);color:#c6fff6}
.badge-mini.off{background:rgba(148,163,184,.08)}
.badge-mini.active{background:rgba(239,68,68,.16);border-color:rgba(239,68,68,.4);color:#ffd4d4}
.badge-mini.idle{background:rgba(148,163,184,.08)}
@keyframes flow{0%{stroke-dashoffset:0}100%{stroke-dashoffset:-36}}
</style>
