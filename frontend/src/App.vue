<template>
  <div style="padding:24px; font-family: system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, 'Helvetica Neue', 'Noto Sans', 'Liberation Sans', Arial, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol', 'Noto Color Emoji'">
    <h1>Starnew BI</h1>
    <nav style="margin: 12px 0; display:flex; gap:12px">
      <router-link to="/">Home</router-link>
      <router-link to="/os">OS</router-link>
      <router-link to="/vendas">Vendas</router-link>
      <router-link to="/locacoes">Locações</router-link>
    </nav>
    <router-view />
  </div>
</template>

<script setup>
</script>
