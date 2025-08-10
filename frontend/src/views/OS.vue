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
      <div>
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

const statusOptions = computed(() => ({
  labels: statusLabels.value,
  legend: { position: 'bottom' }
}))
const volumeOptions = computed(() => ({
  xaxis: { categories: volumeCats.value },
  dataLabels: { enabled: false },
  stroke: { curve: 'smooth' }
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
async function loadAll() {
  await Promise.all([loadStatus(), loadVolume(), loadTmc()])
}

onMounted(() => { loadAll() })

</script>

<script>
export default {
  components: { apexchart: VueApexCharts }
}
</script>
