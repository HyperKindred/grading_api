<template>
  <el-container style="min-height: 100vh;">
    <!-- 左侧可收缩菜单 -->
    <el-aside :width="asideWidth" style="background-color: #f5f5f5; transition: width 0.3s;">
      <div style="padding: 20px; text-align: right;">
        <el-button @click="toggleAside" :icon="isCollapse ? 'Expand' : 'Fold'">
          {{ isCollapse ? '展开' : '收起' }}
        </el-button>
      </div>
      <el-menu
        :collapse="isCollapse"
        :collapse-transition="false"
        router
        default-active="/"
        style="border-right: none;"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-sub-menu index="problems">
          <template #title>
            <el-icon><List /></el-icon>
            <span>题目列表</span>
          </template>
          <el-menu-item
            v-for="problem in problems"
            :key="problem.id"
            :index="`/problem/${problem.id}`"
          >
            {{ problem.title }}
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <!-- 右侧主内容区 -->
    <el-container>
      <el-header style="background-color: #fff; border-bottom: 1px solid #ddd; display: flex; align-items: center;">
        <h2 style="margin: 0;">智能代码批改系统</h2>
      </el-header>
      <el-main style="height: calc(100vh - 60px); overflow-y: auto;">
        <router-view :problems="problems" @update-problems="fetchProblems" />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { HomeFilled, List } from '@element-plus/icons-vue'
import { getProblems } from './api'

const problems = ref([])
const isCollapse = ref(false)
const asideWidth = computed(() => (isCollapse.value ? '64px' : '240px'))

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

onMounted(fetchProblems)
</script>

<style>
body {
  margin: 0;
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
</style>