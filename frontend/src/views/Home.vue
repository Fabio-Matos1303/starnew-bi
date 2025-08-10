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
      <button @click="load">Atualizar</button>
    </div>

    <div style="display:grid; grid-template-columns: repeat(3, 1fr); gap: 16px; margin-bottom: 16px">
      <div class="kpi">
        <div class="kpi-title">Receita total</div>
        <div class="kpi-value">R$ {{ Number(data.receita_total || 0).toFixed(2) }}</div>
      </div>
      <div class="kpi">
        <div class="kpi-title">Novos clientes</div>
        <div class="kpi-value">{{ data.novos_clientes || 0 }}</div>
      </div>
      <div class="kpi">
        <div class="kpi-title">Participação (Vendas/OS/Locações)</div>
        <div class="kpi-value">{{ parts }}</div>
      </div>
    </div>

    <div style="display:grid; grid-template-columns: 1fr 1fr; gap: 16px">
      <div>
        <h3>Participação</h3>
        <div v-if="loading">Carregando...</div>
        <div v-else-if="partSeries.length===0">Sem dados</div>
        <apexchart v-else type="donut" height="300" :options="partOptions" :series="partSeries" />
        <div v-if="error" style="color:#b00">{{ error }}</div>
      </div>
      <div>
        <h3>Status de OS</h3>
        <div v-if="loading">Carregando...</div>
        <div v-else-if="!osStatusSeries[0]?.data?.length">Sem dados</div>
        <apexchart v-else type="bar" height="300" :options="osStatusOptions" :series="osStatusSeries" />
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
const data = ref({ receita_total: 0, participacao: {}, novos_clientes: 0, os_status: {} })
const loading = ref(false)
const error = ref('')
const parts = computed(() => {
  const p = data.value.participacao || {}
  return `V ${Number(p.vendas||0).toFixed(2)} | OS ${Number(p.os||0).toFixed(2)} | L ${Number(p.locacoes||0).toFixed(2)}`
})

const partLabels = ['Vendas','OS','Locações']
const partSeries = computed(() => {
  const p = data.value.participacao || {}
  const arr = [Number(p.vendas||0), Number(p.os||0), Number(p.locacoes||0)]
  return arr.every(v => v===0) ? [] : arr
})
const partOptions = { labels: partLabels, legend: { position: 'bottom' } }

const osStatusCats = computed(() => Object.keys(data.value.os_status || {}))
const osStatusSeries = computed(() => [{ name: 'OS', data: Object.values(data.value.os_status || {}) }])
const osStatusOptions = computed(() => ({ xaxis: { categories: osStatusCats.value }, dataLabels: { enabled: false } }))

async function load() {
  loading.value = true; error.value = ''
  try {
    const res = await axios.get('/api/v1/kpi/geral', { params: { from: from.value, to: to.value } })
    data.value = res.data
  } catch (e) {
    error.value = e?.message || String(e)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<style scoped>
.kpi { border: 1px solid #e0e0e0; padding: 12px; border-radius: 6px }
.kpi-title { color:#666; font-size: 12px }
.kpi-value { font-size: 20px; font-weight: 600 }
</style>

<script>
export default { components: { apexchart: VueApexCharts } }
</script>
