<template>
  <!-- 登录页面：无侧边栏和顶部栏，全屏居中 -->
  <div v-if="isLoginPage" class="full-page-login">
    <router-view />
  </div>

  <!-- 其他页面：正常布局 -->
  <el-container v-else style="min-height: 100vh;">
    <el-aside :width="asideWidth" style="background-color: #f5f5f5; transition: width 0.3s;">
      <div style="padding: 20px; text-align: right;">
        <el-button style="width: 20px;" @click="toggleAside" :icon="isCollapse ? 'Expand' : 'Fold'">
        </el-button>
      </div>
      <el-menu
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        :default-active="$route.path"
        style="border-right: none;"
      >
        <el-sub-menu index="problems">
          <template #title>
            <el-icon><List /></el-icon>
            <span>题目列表</span>
          </template>
          <el-menu-item
            v-for="problem in problems"
            :key="problem.id"
            :index="user?.role === 'teacher' ? `/teacher/problem/${problem.id}` : `/problem/${problem.id}`"
          >
            {{ problem.title }}
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header style="background-color: #fff; border-bottom: 1px solid #ddd; display: flex; align-items: center; justify-content: space-between;">
        <h2 style="margin: 0;">智能代码批改系统</h2>
        <div v-if="user" class="user-info">
          <span>{{ user.name }} ({{ user.role === 'student' ? user.sid : '教师' }})</span>
          <el-button type="text" @click="logout" style="margin-left: 15px;">退出登录</el-button>
        </div>
      </el-header>
      <el-main style="height: calc(100vh - 60px); overflow-y: auto;">
        <router-view :problems="problems" @update-problems="fetchProblems" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { HomeFilled, List, Setting } from '@element-plus/icons-vue'
import { getProblems } from './api'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const problems = ref([])
const isCollapse = ref(false)
const asideWidth = computed(() => (isCollapse.value ? '64px' : '240px'))

// 判断是否是登录页
const isLoginPage = computed(() => route.path === '/login')

// 用户信息
const user = ref(null)
const isTeacher = computed(() => user.value?.role === 'teacher')

const updateUser = () => {
  const u = localStorage.getItem('user')
  user.value = u ? JSON.parse(u) : null
}

const fetchProblems = async () => {
  try {
    const res = await getProblems()
    problems.value = res.data
  } catch (err) {
    console.error('获取题目列表失败', err)
  }
}

const toggleAside = () => {
  isCollapse.value = !isCollapse.value
}

const logout = () => {
  localStorage.removeItem('user')
  localStorage.removeItem('students')
  updateUser()
  router.push('/login')
  ElMessage.success('已退出登录')
}

// 检查登录状态
const checkLogin = () => {
  const u = localStorage.getItem('user')
  if (u) {
    user.value = JSON.parse(u)
  } else if (route.path !== '/login') {
    router.push('/login')
  }
}

onMounted(() => {
  fetchProblems()
  checkLogin()
  updateUser()
})

watch(() => route.path, () => {
  updateUser()
})
</script>

<style>
body {
  margin: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.user-info {
  font-size: 14px;
  color: #333;
}

/* 登录页全屏背景 */
.full-page-login {
  height: 100vh;
  background: #f0f2f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 左侧按钮对齐 */
.el-aside > div:first-child {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;
  box-sizing: border-box;
}
.el-header {
  padding: 0 20px;
}
</style>