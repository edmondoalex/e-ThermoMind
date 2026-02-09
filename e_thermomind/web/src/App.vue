<template>
  <div class="wrap">
    <header class="top">
      <div class="brand">e-ThermoMind</div>
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
          <div class="kpi"><div class="k">T_ACS</div><div class="v">{{ fmtTemp(d.inputs.t_acs) }}</div></div>
          <div class="kpi"><div class="k">T_Puffer</div><div class="v">{{ fmtTemp(d.inputs.t_puffer) }}</div></div>
          <div class="kpi"><div class="k">T_Volano</div><div class="v">{{ fmtTemp(d.inputs.t_volano) }}</div></div>
          <div class="kpi"><div class="k">Export rete</div><div class="v">{{ fmtW(d.inputs.grid_export_w) }}</div></div>
        </div>

        <div class="statusline">
          <span class="muted">v{{ status?.version || '-' }}</span>
          <span class="badge" :class="status?.ha_connected ? 'ok' : 'off'">
            {{ status?.ha_connected ? 'Online' : 'Offline' }}
          </span>
          <span class="muted">HA</span>
          <span class="muted">Ultimo aggiornamento: {{ lastUpdate ? lastUpdate.toLocaleTimeString() : '-' }}</span>
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

        <div class="actions">
          <button @click="refresh">Aggiorna</button>
        </div>
      </section>

      <section v-else class="card">
        <h2>Admin (v0.2)</h2>
        <p class="muted">Setpoint interni e mapping entita HA.</p>
        <div class="statusline">
          <span class="muted">v{{ status?.version || '-' }}</span>
          <span class="badge" :class="status?.ha_connected ? 'ok' : 'off'">
            {{ status?.ha_connected ? 'Online' : 'Offline' }}
          </span>
          <span class="muted">HA</span>
          <span class="muted">Ultimo aggiornamento: {{ lastUpdate ? lastUpdate.toLocaleTimeString() : '-' }}</span>
        </div>

        <div v-if="sp" class="form">
          <h3 class="section">Setpoint</h3>
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

        <div v-if="ent" class="form">
          <h3 class="section">Entita Home Assistant</h3>
          <div class="field"><label>T_ACS</label><input type="text" v-model="ent.t_acs" placeholder="sensor.acs_temp"/></div>
          <div class="field"><label>T_Puffer</label><input type="text" v-model="ent.t_puffer" placeholder="sensor.puffer_temp"/></div>
          <div class="field"><label>T_Volano</label><input type="text" v-model="ent.t_volano" placeholder="sensor.volano_temp"/></div>
          <div class="field"><label>T_Solare mandata</label><input type="text" v-model="ent.t_solare_mandata" placeholder="sensor.solar_mandata"/></div>
          <div class="field"><label>Export rete (W)</label><input type="text" v-model="ent.grid_export_w" placeholder="sensor.grid_export_w"/></div>
        </div>

        <div v-if="act" class="form">
          <h3 class="section">Attuatori Home Assistant</h3>
          <div class="field"><label>Pompa ACS</label><input type="text" v-model="act.pump_acs.entity_id" placeholder="switch.pump_acs"/></div>
          <div class="field"><label>Valvola ACS</label><input type="text" v-model="act.valve_acs.entity_id" placeholder="switch.valve_acs"/></div>
          <div class="field"><label>Pompa Puffer</label><input type="text" v-model="act.pump_puffer.entity_id" placeholder="switch.pump_puffer"/></div>
          <div class="field"><label>Valvola Puffer</label><input type="text" v-model="act.valve_puffer.entity_id" placeholder="switch.valve_puffer"/></div>
          <div class="field"><label>Pompa Volano</label><input type="text" v-model="act.pump_volano.entity_id" placeholder="switch.pump_volano"/></div>
          <div class="field"><label>Valvola Volano</label><input type="text" v-model="act.valve_volano.entity_id" placeholder="switch.valve_volano"/></div>
          <div class="field"><label>Resistenza 1</label><input type="text" v-model="act.resistance_1.entity_id" placeholder="switch.resistance_1"/></div>
          <div class="field"><label>Resistenza 2</label><input type="text" v-model="act.resistance_2.entity_id" placeholder="switch.resistance_2"/></div>
          <div class="field"><label>Resistenza 3</label><input type="text" v-model="act.resistance_3.entity_id" placeholder="switch.resistance_3"/></div>
          <div class="actions">
            <button class="ghost" @click="saveActuators">Salva attuatori</button>
          </div>
        </div>

        <div v-if="act" class="form">
          <h3 class="section">Comandi manuali</h3>
          <div class="row3">
            <button class="ghost" @click="doAct(act.pump_acs.entity_id, 'on')">Pompa ACS ON</button>
            <button class="ghost" @click="doAct(act.pump_acs.entity_id, 'off')">Pompa ACS OFF</button>
            <div class="muted">{{ act.pump_acs.state || '-' }}</div>
          </div>
          <div class="row3">
            <button class="ghost" @click="doAct(act.pump_puffer.entity_id, 'on')">Pompa Puffer ON</button>
            <button class="ghost" @click="doAct(act.pump_puffer.entity_id, 'off')">Pompa Puffer OFF</button>
            <div class="muted">{{ act.pump_puffer.state || '-' }}</div>
          </div>
          <div class="row3">
            <button class="ghost" @click="doAct(act.pump_volano.entity_id, 'on')">Pompa Volano ON</button>
            <button class="ghost" @click="doAct(act.pump_volano.entity_id, 'off')">Pompa Volano OFF</button>
            <div class="muted">{{ act.pump_volano.state || '-' }}</div>
          </div>
          <div class="row3">
            <button class="ghost" @click="doAct(act.resistance_1.entity_id, 'on')">Resistenza 1 ON</button>
            <button class="ghost" @click="doAct(act.resistance_1.entity_id, 'off')">Resistenza 1 OFF</button>
            <div class="muted">{{ act.resistance_1.state || '-' }}</div>
          </div>
          <div class="row3">
            <button class="ghost" @click="doAct(act.resistance_2.entity_id, 'on')">Resistenza 2 ON</button>
            <button class="ghost" @click="doAct(act.resistance_2.entity_id, 'off')">Resistenza 2 OFF</button>
            <div class="muted">{{ act.resistance_2.state || '-' }}</div>
          </div>
          <div class="row3">
            <button class="ghost" @click="doAct(act.resistance_3.entity_id, 'on')">Resistenza 3 ON</button>
            <button class="ghost" @click="doAct(act.resistance_3.entity_id, 'off')">Resistenza 3 OFF</button>
            <div class="muted">{{ act.resistance_3.state || '-' }}</div>
          </div>
        </div>

        <div class="actions">
          <button @click="save">Salva setpoint</button>
          <button class="ghost" @click="saveEntities">Salva entita</button>
          <button class="ghost" @click="loadAll">Ricarica</button>
        </div>
      </section>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
const tab = ref('user')
const d = ref(null)
const sp = ref(null)
const ent = ref(null)
const act = ref(null)
const status = ref(null)
let pollTimer = null
const lastUpdate = ref(null)
const pollMs = ref(3000)

const fmtTemp = (v) => (Number.isFinite(v) ? `${v.toFixed(1)}C` : 'n/d')
const fmtW = (v) => (Number.isFinite(v) ? `${Math.round(v)} W` : 'n/d')

async function refresh(){
  const r = await fetch('/api/decision'); d.value = await r.json()
  const s = await fetch('/api/status'); status.value = await s.json()
  lastUpdate.value = new Date()
}
async function load(){
  const r = await fetch('/api/setpoints'); sp.value = await r.json()
  if (sp.value?.runtime?.ui_poll_ms) {
    pollMs.value = Number(sp.value.runtime.ui_poll_ms) || 3000
  }
}
async function loadActuators(){
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
async function loadEntities(){
  const r = await fetch('/api/entities'); ent.value = await r.json()
}
async function saveEntities(){
  await fetch('/api/entities',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({entities: ent.value})})
  await refresh()
}
async function saveActuators(){
  await fetch('/api/actuators',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({actuators: act.value})})
  await loadActuators()
}
async function doAct(entity_id, action){
  if (!entity_id) return
  await fetch('/api/actuate',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({entity_id, action})})
  await loadActuators()
}
async function loadAll(){
  await load()
  await loadEntities()
  await loadActuators()
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
onMounted(async()=>{ await loadAll(); startPolling() })
onBeforeUnmount(()=>{ stopPolling() })
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
.field input{width:100%;padding:10px;border-radius:12px;border:1px solid var(--border);background:#0f1522;color:var(--text)}
.row3{display:grid;grid-template-columns:repeat(3,1fr);gap:8px}
.statusline{display:flex;align-items:center;gap:8px;margin:8px 0 12px 0;flex-wrap:wrap}
.badge{font-size:12px;padding:4px 8px;border-radius:999px;border:1px solid var(--border)}
.badge.ok{color:#0b1f1c;background:var(--accent)}
.badge.off{color:#f5f7fa;background:#3b3f46}
</style>
