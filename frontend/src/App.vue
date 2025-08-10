<template>
  <div style="padding:24px; font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', 'Noto Sans', 'Liberation Sans', Arial, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'">
    <h1>Starnew BI</h1>
    <p>Ambiente inicial pronto. Faça o teste de saúde da API abaixo.</p>
    <button @click="checkHealth">Testar API /api/v1/health</button>
    <pre v-if="health">{{ health }}</pre>
  </div>
</template>

<script setup>
import axios from 'axios'
import { ref } from 'vue'

const health = ref('')
async function checkHealth() {
  try {
    const { data } = await axios.get('/api/v1/health')
    health.value = JSON.stringify(data, null, 2)
  } catch (e) {
    health.value = e?.message || String(e)
  }
}
</script>
