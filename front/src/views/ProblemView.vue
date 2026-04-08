<template>
  <el-row :gutter="20" style="height: 100%;">
    <!-- 左侧：题目详情 -->
    <el-col :span="10" style="height: 100%; overflow-y: auto;">
      <el-card v-if="!loading" style="height: 100%;">
        <template #header>
          <h2>{{ problem.title }}</h2>
        </template>
        <div class="description" v-html="formattedDescription"></div>
      </el-card>
      <el-skeleton v-else :rows="10" animated />
    </el-col>

    <!-- 右侧：代码编辑器 + 按钮 -->
    <el-col :span="14" style="height: 100%; display: flex; flex-direction: column;">
      <el-card style="height: 100%; margin-bottom: 10px;">
        <template #header>
          <span>代码编辑区</span>
        </template>
        <MonacoEditor
          v-model:value="code"
          language="python"
          :options="editorOptions"
          style="height: 500px; border: 1px solid #ccc; border-radius: 5px;"
        />
        <div style="margin-top: 10px; text-align: right;">
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ submitting ? '评测中' : '提交评测' }}
          </el-button>
          <el-button 
            type="success" 
            @click="showResultDialog = true" 
            :disabled="!result"
            style="margin-left: 10px;">
            查看结果
          </el-button>
        </div>
      </el-card>
      <!-- 原评测结果卡片已移除，改为弹窗 -->
    </el-col>
  </el-row>

  <!-- 结果弹窗 -->
  <el-dialog
    v-model="showResultDialog"
    title="📊 评测结果"
    width="70%"
    :close-on-click-modal="false"
    destroy-on-close
  >
    <ResultDisplay :result="result" />
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import MonacoEditor from '@guolao/vue-monaco-editor'
import { getProblem, submitCode } from '../api'
import ResultDisplay from '../components/ResultDisplay.vue'
import { ElMessage } from 'element-plus'

const route = useRoute()
const problemId = route.params.id

const problem = ref({})
const code = ref('')
const loading = ref(true)
const submitting = ref(false)
const result = ref(null)
const showResultDialog = ref(false)  // 控制弹窗显示

const editorOptions = {
  automaticLayout: true,
  fontSize: 14,
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
}

const formattedDescription = computed(() => {
  return problem.value.description?.replace(/\n/g, '<br>') || ''
})

onMounted(async () => {
  try {
    const res = await getProblem(problemId)
    problem.value = res.data
    code.value = '# 请在这里编写你的代码\n'
  } catch (err) {
    console.error('获取题目详情失败', err)
    ElMessage.error('加载题目失败')
  } finally {
    loading.value = false
  }
})

const handleSubmit = async () => {
  submitting.value = true
  try {
    const res = await submitCode(problemId, code.value)
    result.value = res.data
    ElMessage.success('评测完成，点击“查看结果”查看详情')
  } catch (err) {
    console.error('提交失败', err)
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.description {
  white-space: pre-wrap;
  line-height: 1.6;
  font-size: 16px;
}
.el-row {
  height: 100%;
}
.el-col {
  height: 100%;
}
</style>