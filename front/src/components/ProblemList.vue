<template>
  <div class="problem-list">
    <h2>题目列表</h2>
    <ul>
      <li v-for="problem in problems" :key="problem.id">
        <router-link :to="`/problem/${problem.id}`">
          {{ problem.title }}
          <span class="difficulty" :class="problem.difficulty">{{ problem.difficulty }}</span>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getProblems } from '../api'

const problems = ref([])

onMounted(async () => {
  try {
    const res = await getProblems()
    problems.value = res.data
  } catch (err) {
    console.error('获取题目列表失败', err)
  }
})
</script>

<style scoped>
.problem-list ul {
  list-style: none;
  padding: 0;
}
.problem-list li {
  margin: 15px 0;
  padding: 10px;
  border: 1px solid #eee;
  border-radius: 5px;
  transition: 0.2s;
}
.problem-list li:hover {
  background: #f9f9f9;
}
.difficulty {
  margin-left: 10px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.8em;
  color: white;
}
.difficulty.easy { background: #4caf50; }
.difficulty.medium { background: #ff9800; }
.difficulty.hard { background: #f44336; }
</style>