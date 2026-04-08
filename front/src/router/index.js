import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import ProblemView from '../views/ProblemView.vue'

const routes = [
  { path: '/', name: 'home', component: HomeView },
  { path: '/problem/:id', name: 'problem', component: ProblemView, props: true },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router