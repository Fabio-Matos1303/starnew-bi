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

    <div>
      <h3>Status de OS</h3>
      <pre style="background:#f7f7f7; padding:8px">{{ JSON.stringify(data.os_status || {}, null, 2) }}</pre>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const from = ref('')
const to = ref('')
const data = ref({ receita_total: 0, participacao: {}, novos_clientes: 0, os_status: {} })
const parts = computed(() => {
  const p = data.value.participacao || {}
  return `V ${Number(p.vendas||0).toFixed(2)} | OS ${Number(p.os||0).toFixed(2)} | L ${Number(p.locacoes||0).toFixed(2)}`
})

async function load() {
  const res = await axios.get('/api/v1/kpi/geral', { params: { from: from.value, to: to.value } })
  data.value = res.data
}

onMounted(load)
</script>

<style scoped>
.kpi { border: 1px solid #e0e0e0; padding: 12px; border-radius: 6px }
.kpi-title { color:#666; font-size: 12px }
.kpi-value { font-size: 20px; font-weight: 600 }
</style>
