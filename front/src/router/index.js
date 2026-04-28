import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import StudentView from '../views/StudentView.vue'
import TeacherView from '../views/TeacherView.vue'

const routes = [
  { path: '/login', component: Login },
  {
    path: '/',
    redirect: () => {
      const user = JSON.parse(localStorage.getItem('user') || 'null')
      if (user?.role === 'teacher') {
        // 教师默认跳转到第一道题的教师视图（假设题目 test1 存在）
        return '/teacher/problem/test1'
      } else {
        return '/problem/test1'
      }
    }
  },
  {
    path: '/problem/:id',
    component: StudentView,
    meta: { requiresAuth: true, role: 'student' }
  },
  {
    path: '/teacher/problem/:id',
    component: TeacherView,
    meta: { requiresAuth: true, role: 'teacher' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const user = JSON.parse(localStorage.getItem('user') || 'null')
  if (to.meta.requiresAuth) {
    if (!user) {
      next('/login')
    } else if (to.meta.role && user.role !== to.meta.role) {
      // 角色不匹配，重定向到合适的首页
      if (user.role === 'student') {
        next('/problem/test1')
      } else {
        next('/teacher/problem/test1')
      }
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router