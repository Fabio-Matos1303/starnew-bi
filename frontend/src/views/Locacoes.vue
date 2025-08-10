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

    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 16px">
      <div>
        <h3>Faturamento total</h3>
        <div class="kpi">R$ {{ Number(faturamento.total||0).toFixed(2) }}</div>
      </div>
      <div>
        <h3>Taxa de ocupação</h3>
        <div class="kpi">{{ taxa.taxa==null ? '—' : (Number(taxa.taxa*100).toFixed(1)+'%') }} ({{ taxa.ocupados||0 }}/{{ taxa.ativos||0 }})</div>
      </div>
      <div style="grid-column: 1 / -1">
        <h3>Faturamento por dia</h3>
        <div v-if="loading.faturamento">Carregando...</div>
        <div v-else-if="!fatSeries[0]?.data?.length">Sem dados</div>
        <apexchart v-else type="line" height="320" :options="fatOptions" :series="fatSeries" />
      </div>
      <div style="grid-column: 1 / -1">
        <h3>Top itens</h3>
        <div v-if="loading.top">Carregando...</div>
        <div v-else-if="!topSeries[0]?.data?.length">Sem dados</div>
        <apexchart v-else type="bar" height="320" :options="topOptions" :series="topSeries" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import VueApexCharts from 'vue3-apexcharts'

const from = ref('')
const to = ref('')
const faturamento = ref({ total: 0, por_dia: [] })
const taxa = ref({ ativos: 0, ocupados: 0, taxa: null })
const top = ref([])
const loading = ref({ faturamento: false, top: false, taxa: false })

const fatCats = computed(() => faturamento.value.por_dia.map(x => x.dia))
const fatSeries = computed(() => [{ name: 'Locações', data: faturamento.value.por_dia.map(x => x.total) }])
const fatOptions = computed(() => ({ xaxis: { categories: fatCats.value }, dataLabels: { enabled: false }, stroke: { curve: 'smooth' } }))

const topLabels = computed(() => top.value.map(x => x.descricao))
const topSeries = computed(() => [{ name: 'Receita', data: top.value.map(x => x.total_receita) }])
const topOptions = computed(() => ({ xaxis: { categories: topLabels.value }, plotOptions: { bar: { horizontal: true } }, dataLabels: { enabled: false } }))

async function loadFaturamento() {
  loading.value.faturamento = true
  try {
    const { data } = await axios.get('/api/v1/locacoes/faturamento', { params: { from: from.value, to: to.value } })
    faturamento.value = data
  } finally {
    loading.value.faturamento = false
  }
}
async function loadTop() {
  loading.value.top = true
  try {
    const { data } = await axios.get('/api/v1/locacoes/top-itens', { params: { from: from.value, to: to.value } })
    top.value = data
  } finally {
    loading.value.top = false
  }
}
async function loadTaxa() {
  loading.value.taxa = true
  try {
    const { data } = await axios.get('/api/v1/locacoes/taxa-ocupacao')
    taxa.value = data
  } finally {
    loading.value.taxa = false
  }
}
async function loadAll() {
  await Promise.all([loadFaturamento(), loadTop(), loadTaxa()])
}

onMounted(loadAll)
</script>

<script>
export default { components: { apexchart: VueApexCharts } }
</script>

<style scoped>
.kpi { border: 1px solid #e0e0e0; padding: 12px; border-radius: 6px; font-weight: 600 }
</style>
