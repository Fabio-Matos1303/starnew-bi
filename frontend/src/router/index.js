import { createRouter, createWebHistory } from 'vue-router'
import OS from '../views/OS.vue'
import Home from '../views/Home.vue'

const routes = [
  { path: '/', name: 'Home', component: Home },
  { path: '/os', name: 'OS', component: OS },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
