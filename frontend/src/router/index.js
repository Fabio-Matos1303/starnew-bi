import { createRouter, createWebHistory } from 'vue-router'
import OS from '../views/OS.vue'
import Home from '../views/Home.vue'
import Vendas from '../views/Vendas.vue'
import Locacoes from '../views/Locacoes.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/os', name: 'OS', component: OS },
  { path: '/vendas', name: 'Vendas', component: Vendas },
  { path: '/locacoes', name: 'Locações', component: Locacoes },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
