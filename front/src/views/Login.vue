<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>智能代码批改系统</h2>
      </template>
      <el-select v-model="selectedUserId" placeholder="请选择用户" size="large" style="width: 100%;">
        <el-option
          v-for="user in userList"
          :key="user.id"
          :label="`${user.name} (${user.role === 'student' ? user.sid : '教师'})`"
          :value="user.id"
        />
      </el-select>
      <el-button type="primary" @click="handleLogin" style="margin-top: 20px; width: 100%;">
        登录
      </el-button>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getUsers, login } from '../api'

const router = useRouter()
const selectedUserId = ref(null)
const userList = ref([])

onMounted(async () => {
  try {
    const res = await getUsers()
    userList.value = res.data
  } catch (err) {
    console.error('获取用户列表失败', err)
    ElMessage.error('获取用户列表失败')
  }
})

const handleLogin = async () => {
  if (!selectedUserId.value) {
    ElMessage.warning('请选择用户')
    return
  }
  try {
    const res = await login(selectedUserId.value)
    localStorage.setItem('user', JSON.stringify(res.data.user))
    if (res.data.user.role === 'teacher') {
      localStorage.setItem('students', JSON.stringify(res.data.students))
    }
    router.push('/')
    ElMessage.success(`欢迎，${res.data.user.name}`)
  } catch (err) {
    ElMessage.error('登录失败')
  }
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background: #f0f2f5;
}
.login-card {
  width: 400px;
}
</style>