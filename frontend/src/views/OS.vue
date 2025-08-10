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
        <apexchart type="donut" height="300" :options="statusOptions" :series="statusSeries" />
      </div>
      <div>
        <h3>Tempo médio de conclusão (dias)</h3>
        <div style="font-size:28px; font-weight:600">{{ tmc?.dias ?? '—' }}</div>
        <div style="color:#666">Amostras: {{ tmc?.amostras ?? 0 }}</div>
      </div>
      <div style="grid-column: 1 / -1">
        <h3>Volume por dia</h3>
        <apexchart type="line" height="320" :options="volumeOptions" :series="volumeSeries" />
      </div>
      <div>
        <h3>Top serviços</h3>
        <apexchart type="bar" height="320" :options="topServOptions" :series="topServSeries" />
      </div>
      <div style="grid-column: 1 / -1">
        <h3>Listagem</h3>
        <div style="margin:8px 0; color:#666">Filtro status: <strong>{{ statusFilter || 'Todos' }}</strong></div>
        <table border="1" cellspacing="0" cellpadding="6" width="100%">
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
  const { data } = await axios.get('/api/v1/os/status', { params: { from: from.value, to: to.value } })
  statusLabels.value = Object.keys(data.distribuicao)
  statusSeries.value = Object.values(data.distribuicao)
}
async function loadVolume() {
  const { data } = await axios.get('/api/v1/os/volume', { params: { from: from.value, to: to.value } })
  volumeCats.value = data.por_dia.map(x => x.dia)
  volumeSeries.value = [{ name: 'OS', data: data.por_dia.map(x => x.total) }]
}
async function loadTmc() {
  const { data } = await axios.get('/api/v1/os/tempo-medio-conclusao', { params: { from: from.value, to: to.value } })
  tmc.value = data
}
async function loadTopServ() {
  const { data } = await axios.get('/api/v1/os/top-servicos', { params: { from: from.value, to: to.value } })
  topServLabels.value = data.map(x => x.descricao)
  topServSeries.value = [{ name: 'Receita', data: data.map(x => x.total_receita) }]
}
async function loadList() {
  const { data } = await axios.get('/api/v1/os/list', { params: { from: from.value, to: to.value, status: statusFilter.value || undefined, limit: limit.value, offset: offset.value } })
  items.value = data.items
  total.value = data.total
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
