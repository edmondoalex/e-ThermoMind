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
          <div class="kpi">
            <div class="k"><i v-if="mdiClass(ent?.t_acs?.attributes?.icon)" :class="mdiClass(ent?.t_acs?.attributes?.icon)"></i> T_ACS</div>
            <div class="v">{{ fmtTemp(d.inputs.t_acs) }}</div>
          </div>
          <div class="kpi">
            <div class="k"><i v-if="mdiClass(ent?.t_puffer?.attributes?.icon)" :class="mdiClass(ent?.t_puffer?.attributes?.icon)"></i> T_Puffer</div>
            <div class="v">{{ fmtTemp(d.inputs.t_puffer) }}</div>
          </div>
          <div class="kpi">
            <div class="k"><i v-if="mdiClass(ent?.t_volano?.attributes?.icon)" :class="mdiClass(ent?.t_volano?.attributes?.icon)"></i> T_Volano</div>
            <div class="v">{{ fmtTemp(d.inputs.t_volano) }}</div>
          </div>
          <div class="kpi">
            <div class="k"><i v-if="mdiClass(ent?.grid_export_w?.attributes?.icon)" :class="mdiClass(ent?.grid_export_w?.attributes?.icon)"></i> Export rete</div>
            <div class="v">{{ fmtW(d.inputs.grid_export_w) }}</div>
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
        </div>

        <div v-if="act" class="card inner">
          <div class="row"><strong>Resistenze volano</strong></div>
          <div class="row3">
            <div class="kpi" :class="stateClass(act?.r22_resistenza_1_volano_pdc?.state)">
              <div class="k">
                <i v-if="mdiClass(act?.r22_resistenza_1_volano_pdc?.attributes?.icon)" :class="[mdiClass(act?.r22_resistenza_1_volano_pdc?.attributes?.icon), stateClass(act?.r22_resistenza_1_volano_pdc?.state)]"></i>
                R22 Resistenza 1 Volano PDC
              </div>
            </div>
            <div class="kpi" :class="stateClass(act?.r23_resistenza_2_volano_pdc?.state)">
              <div class="k">
                <i v-if="mdiClass(act?.r23_resistenza_2_volano_pdc?.attributes?.icon)" :class="[mdiClass(act?.r23_resistenza_2_volano_pdc?.attributes?.icon), stateClass(act?.r23_resistenza_2_volano_pdc?.state)]"></i>
                R23 Resistenza 2 Volano PDC
              </div>
            </div>
            <div class="kpi" :class="stateClass(act?.r24_resistenza_3_volano_pdc?.state)">
              <div class="k">
                <i v-if="mdiClass(act?.r24_resistenza_3_volano_pdc?.attributes?.icon)" :class="[mdiClass(act?.r24_resistenza_3_volano_pdc?.attributes?.icon), stateClass(act?.r24_resistenza_3_volano_pdc?.state)]"></i>
                R24 Resistenza 3 Volano PDC
              </div>
            </div>
            <div class="kpi">
              <div class="k">
                <i v-if="mdiClass(ent?.resistenze_volano_power?.attributes?.icon)" :class="mdiClass(ent?.resistenze_volano_power?.attributes?.icon)"></i>
                Potenza Resistenze
              </div>
              <div class="v">{{ fmtEntity(ent?.resistenze_volano_power) }}</div>
            </div>
            <div class="kpi">
              <div class="k">
                <i v-if="mdiClass(ent?.resistenze_volano_energy?.attributes?.icon)" :class="mdiClass(ent?.resistenze_volano_energy?.attributes?.icon)"></i>
                Energia Resistenze
              </div>
              <div class="v">{{ fmtEntity(ent?.resistenze_volano_energy) }}</div>
            </div>
          </div>
        </div>

        <div class="actions">
          <button @click="refresh">Aggiorna</button>
        </div>

        <div v-if="actions.length" class="card inner">
          <div class="row"><strong>Ultime azioni</strong></div>
          <div v-for="(line, idx) in actions.slice().reverse()" :key="`a-${idx}`" class="muted">{{ line }}</div>
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
          <div class="field">
            <label>Runtime mode</label>
            <select v-model="sp.runtime.mode" @change="confirmMode">
              <option value="dry-run">dry-run</option>
              <option value="live">live</option>
            </select>
          </div>
          <div class="field"><label>ACS setpoint (C)</label><input type="number" step="0.5" v-model.number="sp.acs.setpoint_c"/></div>
          <div class="field"><label>ACS MAX (C)</label><input type="number" step="0.5" v-model.number="sp.acs.max_c"/></div>
          <div class="field"><label>Volano margine (C)</label><input type="number" step="0.5" v-model.number="sp.volano.margin_c"/></div>
          <div class="field"><label>Volano MAX (C)</label><input type="number" step="0.5" v-model.number="sp.volano.max_c"/></div>
          <div class="field"><label>Puffer setpoint (C)</label><input type="number" step="0.5" v-model.number="sp.puffer.setpoint_c"/></div>
          <div class="field"><label>Off-delay resistenze (s)</label><input type="number" step="1" v-model.number="sp.resistance.off_delay_s"/></div>
          <div class="field">
            <label>Soglie export (W) [1/2/3]</label>
            <div class="row3">
              <input type="number" v-model.number="sp.resistance.thresholds_w[0]"/>
              <input type="number" v-model.number="sp.resistance.thresholds_w[1]"/>
              <input type="number" v-model.number="sp.resistance.thresholds_w[2]"/>
            </div>
          </div>
          <div class="field">
            <label>Polling UI (ms)</label>
            <input type="number" min="500" step="500" v-model.number="sp.runtime.ui_poll_ms"/>
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
                     @focus="onFocus" @blur="onBlur"/>
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
                     @focus="onFocus" @blur="onBlur"/>
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
                     @focus="onFocus" @blur="onBlur"/>
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
                     @focus="onFocus" @blur="onBlur"/>
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
    </main>
  </div>
</template>

<script setup>
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
const filterAct = ref('')
const editingCount = ref(0)
let focusInHandler = null
let focusOutHandler = null
const modules = ref({
  resistenze_volano: true,
  volano_to_acs: false,
  volano_to_puffer: false,
  puffer_to_acs: false,
  solare: false,
  miscelatrice: false,
  pdc: false
})

const actuatorDefs = [
  { key: 'r1_valve_comparto_laboratorio', label: 'R1 Valvola Comparto Laboratorio (riscaldamento)', impl: false },
  { key: 'r2_valve_comparto_mandata_imp_pt', label: 'R2 Valvola Comparto Mandata Imp PT (riscaldamento)', impl: false },
  { key: 'r3_valve_comparto_mandata_imp_m1p', label: 'R3 Valvola Comparto Mandata Imp M+1P (riscaldamento)', impl: false },
  { key: 'r4_valve_impianto_da_puffer', label: 'R4 Valvola Impianto da Puffer', impl: false },
  { key: 'r5_valve_impianto_da_pdc', label: 'R5 Valvola Impianto da PDC', impl: false },
  { key: 'r6_valve_pdc_to_integrazione_acs', label: 'R6 Valvola PDC -> Integrazione ACS', impl: false },
  { key: 'r7_valve_pdc_to_integrazione_puffer', label: 'R7 Valvola PDC -> Integrazione Puffer', impl: false },
  { key: 'r8_valve_solare_notte_low_temp', label: 'R8 Valvola Solare Notte/Low Temp', impl: false },
  { key: 'r9_valve_solare_normal_funz', label: 'R9 Valvola Solare Normal Funz', impl: false },
  { key: 'r10_valve_solare_precedenza_acs', label: 'R10 Valvola Solare Precedenza ACS', impl: false },
  { key: 'r11_pump_mandata_laboratorio', label: 'R11 Pompa Mandata Laboratorio', impl: false },
  { key: 'r12_pump_mandata_piani', label: 'R12 Pompa Mandata Piani', impl: false },
  { key: 'r13_pump_pdc_to_acs_puffer', label: 'R13 Pompa PDC -> ACS/Puffer', impl: false },
  { key: 'r14_pump_puffer_to_acs', label: 'R14 Pompa Puffer -> ACS', impl: false },
  { key: 'r15_pump_caldaia_legna', label: 'R15 Pompa Caldaia Legna -> Puffer', impl: false },
  { key: 'r16_cmd_miscelatrice_alza', label: 'R16 CMD Miscelatrice ALZA', impl: false },
  { key: 'r17_cmd_miscelatrice_abbassa', label: 'R17 CMD Miscelatrice ABBASSA', impl: false },
  { key: 'r18_valve_ritorno_solare_basso', label: 'R18 Valvola Ritorno Solare Basso', impl: false },
  { key: 'r19_valve_ritorno_solare_alto', label: 'R19 Valvola Ritorno Solare Alto', impl: false },
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

function mergeEntities(next){
  if (!ent.value) { ent.value = next; return }
  for (const key of Object.keys(next || {})) {
    const prev = ent.value[key] || { entity_id: null }
    const keepId = editingCount.value > 0 ? prev.entity_id : next[key]?.entity_id
    ent.value[key] = { ...next[key], entity_id: keepId }
  }
}
function mergeActuators(next){
  if (!act.value) { act.value = next; return }
  for (const key of Object.keys(next || {})) {
    const prev = act.value[key] || { entity_id: null }
    const keepId = editingCount.value > 0 ? prev.entity_id : next[key]?.entity_id
    act.value[key] = { ...next[key], entity_id: keepId }
  }
}
async function refresh(){
  if (tab.value === 'admin' || editingCount.value > 0) return
  const r = await fetch('/api/decision'); d.value = await r.json()
  const s = await fetch('/api/status'); status.value = await s.json()
  const a = await fetch('/api/actions'); actions.value = (await a.json()).items || []
  await loadActuators()
  lastUpdate.value = new Date()
}
async function loadModules(){
  const r = await fetch('/api/modules'); modules.value = await r.json()
}
async function load(){
  const r = await fetch('/api/setpoints'); sp.value = await r.json()
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
function confirmMode(){
  if (!sp.value?.runtime?.mode) return
  if (sp.value.runtime.mode === 'live') {
    const ok = window.confirm('Passare a LIVE? Questo abilita comandi reali agli attuatori.')
    if (!ok) sp.value.runtime.mode = 'dry-run'
  }
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
  await refresh()
}
async function saveActuators(){
  const payload = {}
  for (const item of actuatorDefs) {
    payload[item.key] = act.value?.[item.key]?.entity_id || null
  }
  await fetch('/api/actuators',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({actuators: payload})})
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
async function doAct(entity_id, action){
  if (!entity_id) return
  await fetch('/api/actuate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({entity_id, action})})
  await loadActuators()
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
  doAct(ent.entity_id, action)
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
</script>

<style>
:root{--bg:#0b0f14;--card:#121826;--muted:#9aa4b2;--text:#e6edf3;--accent:#4fd1c5;--border:rgba(255,255,255,.08)}
*{box-sizing:border-box} body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,Noto Sans,sans-serif;background:var(--bg);color:var(--text)}
.wrap{min-height:100vh;display:flex;flex-direction:column}
.top{display:flex;align-items:center;justify-content:space-between;padding:14px 16px;border-bottom:1px solid var(--border);position:sticky;top:0;background:rgba(11,15,20,.9);backdrop-filter:blur(10px)}
.brand{font-weight:700}
.tabs button{background:transparent;color:var(--text);border:1px solid var(--border);padding:8px 10px;border-radius:12px;margin-left:8px;cursor:pointer}
.tabs button.active{border-color:var(--accent);color:var(--accent)}
.main{padding:16px;max-width:980px;margin:0 auto;width:100%}
.card{background:var(--card);border:1px solid var(--border);border-radius:18px;padding:16px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.card.inner{margin-top:14px}
.muted{color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px;margin-top:10px}
@media(min-width:760px){.grid{grid-template-columns:repeat(4,minmax(0,1fr))}}
.kpi{border:1px solid var(--border);border-radius:14px;padding:10px}
.k{font-size:12px;color:var(--muted)} .v{font-size:18px;font-weight:700;margin-top:2px}
.actions{margin-top:14px;display:flex;gap:10px;flex-wrap:wrap}
button{background:var(--accent);border:none;color:#002b2a;padding:10px 12px;border-radius:14px;font-weight:700;cursor:pointer}
button.ghost{background:transparent;border:1px solid var(--border);color:var(--text)}
hr{border:0;border-top:1px solid var(--border);margin:12px 0}
.form{display:grid;gap:10px;margin-top:10px}
.section{margin:6px 0 2px 0;font-size:14px;color:var(--text)}
.field label{display:block;font-size:12px;color:var(--muted);margin-bottom:6px}
.field select{width:100%;padding:10px;border-radius:12px;border:1px solid var(--border);background:#0f1522;color:var(--text)}
.field input{width:100%;padding:10px;border-radius:12px;border:1px solid var(--border);background:#0f1522;color:var(--text)}
.upload{display:inline-flex;align-items:center;gap:8px}
.upload input{display:none}
details.form{border:1px solid var(--border);border-radius:14px;padding:10px;background:rgba(0,0,0,.08)}
details.form summary{cursor:pointer;list-style:none}
.top-actions{display:flex;gap:8px;align-items:center}
.action-btn{background:var(--accent);border:none;color:#002b2a;padding:10px 12px;border-radius:14px;font-weight:700;cursor:pointer}
.action-btn.upload{display:inline-flex;align-items:center;gap:6px}
.setpoint-grid{display:grid;gap:10px}
.setpoint-grid .section{grid-column:1/-1}
@media(min-width:900px){.setpoint-grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
.row3{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.statusline{display:flex;align-items:center;gap:8px;margin:8px 0 12px 0;flex-wrap:wrap}
.badge{font-size:12px;padding:4px 8px;border-radius:999px;border:1px solid var(--border)}
.badge.ok{color:#0b1f1c;background:var(--accent)}
.badge.off{color:#f5f7fa;background:#3b3f46}
.presence{display:inline-block;margin-right:6px}
.presence-ok{color:#22c55e}
.presence-no{color:#ef4444}
.input-ok{border:2px solid #22c55e; box-shadow:0 0 0 2px rgba(34,197,94,0.15)}
.input-row{display:flex;align-items:center;gap:8px}
.logic-dot{display:inline-block}
.logic-ok{color:#22c55e}
.logic-no{color:#ef4444}
.toggle{justify-content:flex-start;gap:8px}
.toggle.on{border-color:rgba(239,68,68,.45);background:rgba(239,68,68,.15);box-shadow:0 0 0 1px rgba(239,68,68,.08) inset}
.toggle.off{border-color:var(--border);background:transparent}
.mdi-fallback{font-size:14px;opacity:0.8}
.state-on{color:#ef4444}
.state-off{color:#94a3b8}
.state-unknown{color:#f59e0b}
.kpi.state-on{border-color:rgba(239,68,68,.45);background:rgba(239,68,68,.08)}
.kpi.state-off{border-color:var(--border)}
.input-on{background:rgba(239,68,68,.12) !important}
.dot-toggle{border:0;background:transparent;cursor:pointer;padding:0 2px}
</style>
