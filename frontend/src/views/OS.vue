<template>
  <div>
    <div style="display:flex; gap:12px; align-items:flex-end; margin-bottom:12px">
      <div>
        <label>De</label>
        <input type="date" v-model="from" />
      </div>
      <div>
        <label>Até</label>
        <input type="date" v-model="to" />
      </div>
      <button @click="loadAll">Atualizar</button>
    </div>

    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px">
      <div @click="onStatusClick" style="cursor:pointer">
        <h3>Status</h3>
        <div v-if="loading.status">Carregando...</div>
        <div v-else-if="statusSeries.length === 0">Sem dados</div>
        <apexchart v-else type="donut" height="300" :options="statusOptions" :series="statusSeries" />
        <div v-if="errors.status" style="color:#b00">{{ errors.status }}</div>
      </div>
      <div>
        <h3>Tempo médio de conclusão (dias)</h3>
        <div v-if="loading.tmc">Carregando...</div>
        <template v-else>
          <div style="font-size:28px; font-weight:600">{{ tmc?.dias ?? '—' }}</div>
          <div style="color:#666">Amostras: {{ tmc?.amostras ?? 0 }}</div>
        </template>
        <div v-if="errors.tmc" style="color:#b00">{{ errors.tmc }}</div>
      </div>
      <div style="grid-column: 1 / -1">
        <h3>Volume por dia</h3>
        <div v-if="loading.volume">Carregando...</div>
        <div v-else-if="!volumeSeries[0]?.data?.length">Sem dados</div>
        <apexchart v-else type="line" height="320" :options="volumeOptions" :series="volumeSeries" />
        <div v-if="errors.volume" style="color:#b00">{{ errors.volume }}</div>
      </div>
      <div>
        <h3>Top serviços</h3>
        <div v-if="loading.top">Carregando...</div>
        <div v-else-if="!topServSeries[0]?.data?.length">Sem dados</div>
        <apexchart v-else type="bar" height="320" :options="topServOptions" :series="topServSeries" />
        <div v-if="errors.top" style="color:#b00">{{ errors.top }}</div>
      </div>
      <div style="grid-column: 1 / -1">
        <h3>Listagem</h3>
        <div style="margin:8px 0; color:#666">Filtro status: <strong>{{ statusFilter || 'Todos' }}</strong></div>
        <div v-if="loading.list">Carregando...</div>
        <template v-else>
          <table v-if="items.length" border="1" cellspacing="0" cellpadding="6" width="100%">
            <thead>
              <tr>
                <th>ID</th>
                <th>Descrição</th>
                <th>Status</th>
                <th>Início</th>
                <th>Fim</th>
                <th>Valor Total</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in items" :key="item.id">
                <td>{{ item.id }}</td>
                <td>{{ item.descricao }}</td>
                <td>{{ item.status }}</td>
                <td>{{ item.data_inicio || '—' }}</td>
                <td>{{ item.data_fim || '—' }}</td>
                <td>R$ {{ Number(item.valor_total).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else>Sem registros</div>
        </template>
        <div v-if="errors.list" style="color:#b00">{{ errors.list }}</div>
        <div style="margin-top:8px; display:flex; gap:8px; align-items:center">
          <button :disabled="offset===0" @click="prevPage">Anterior</button>
          <span>{{ page+1 }}</span>
          <button :disabled="offset+limit >= total" @click="nextPage">Próxima</button>
          <span style="color:#666">Total: {{ total }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import axios from 'axios'
import VueApexCharts from 'vue3-apexcharts'

const from = ref('')
const to = ref('')
const statusSeries = ref([])
const statusLabels = ref([])
const volumeSeries = ref([{ name: 'OS', data: [] }])
const volumeCats = ref([])
const tmc = ref({ dias: null, amostras: 0 })
const topServSeries = ref([{ name: 'Receita', data: [] }])
const topServLabels = ref([])
const items = ref([])
const total = ref(0)
const limit = ref(10)
const offset = ref(0)
const page = computed(() => Math.floor(offset.value / limit.value))
const statusFilter = ref('')

const statusOptions = computed(() => ({
  labels: statusLabels.value,
  legend: { position: 'bottom' }
}))
const volumeOptions = computed(() => ({
  xaxis: { categories: volumeCats.value },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth' }
}))
const topServOptions = computed(() => ({
  xaxis: { categories: topServLabels.value },
  dataLabels: { enabled: false },
  plotOptions: { bar: { horizontal: true } }
}))

async function loadStatus() {
  loading.status = true; errors.status = ''
  try {
    const { data } = await axios.get('/api/v1/os/status', { params: { from: from.value, to: to.value } })
    statusLabels.value = Object.keys(data.distribuicao)
    statusSeries.value = Object.values(data.distribuicao)
  } catch (e) {
    errors.status = e?.message || String(e)
    statusLabels.value = []; statusSeries.value = []
  } finally { loading.status = false }
}
async function loadVolume() {
  loading.volume = true; errors.volume = ''
  try {
    const { data } = await axios.get('/api/v1/os/volume', { params: { from: from.value, to: to.value } })
    volumeCats.value = data.por_dia.map(x => x.dia)
    volumeSeries.value = [{ name: 'OS', data: data.por_dia.map(x => x.total) }]
  } catch (e) {
    errors.volume = e?.message || String(e)
    volumeCats.value = []; volumeSeries.value = [{ name: 'OS', data: [] }]
  } finally { loading.volume = false }
}
async function loadTmc() {
  loading.tmc = true; errors.tmc = ''
  try {
    const { data } = await axios.get('/api/v1/os/tempo-medio-conclusao', { params: { from: from.value, to: to.value } })
    tmc.value = data
  } catch (e) {
    errors.tmc = e?.message || String(e)
    tmc.value = { dias: null, amostras: 0 }
  } finally { loading.tmc = false }
}
async function loadTopServ() {
  loading.top = true; errors.top = ''
  try {
    const { data } = await axios.get('/api/v1/os/top-servicos', { params: { from: from.value, to: to.value } })
    topServLabels.value = data.map(x => x.descricao)
    topServSeries.value = [{ name: 'Receita', data: data.map(x => x.total_receita) }]
  } catch (e) {
    errors.top = e?.message || String(e)
    topServLabels.value = []; topServSeries.value = [{ name: 'Receita', data: [] }]
  } finally { loading.top = false }
}
async function loadList() {
  loading.list = true; errors.list = ''
  try {
    const { data } = await axios.get('/api/v1/os/list', { params: { from: from.value, to: to.value, status: statusFilter.value || undefined, limit: limit.value, offset: offset.value } })
    items.value = data.items
    total.value = data.total
  } catch (e) {
    errors.list = e?.message || String(e)
    items.value = []; total.value = 0
  } finally { loading.list = false }
}
async function loadAll() {
  await Promise.all([loadStatus(), loadVolume(), loadTmc(), loadTopServ(), loadList()])
}

function onStatusClick(event, chartContext, config) {
  const idx = config?.dataPointIndex ?? -1
  if (idx >= 0) {
    statusFilter.value = statusLabels.value[idx]
    offset.value = 0
    loadList()
  }
}

function nextPage() { if (offset.value + limit.value < total.value) { offset.value += limit.value; loadList() } }
function prevPage() { if (offset.value - limit.value >= 0) { offset.value -= limit.value; loadList() } }

onMounted(() => { loadAll() })

</script>

<script>
export default {
  components: { apexchart: VueApexCharts }
}
</script>

<script>
// Local state objects
</script>
