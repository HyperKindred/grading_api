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
      <el-card style="margin-bottom: 10px;">
        <template #header>
          <span>代码编辑区</span>
        </template>
        <MonacoEditor
          v-model:value="code"
          language="python"
          :options="editorOptions"
          style="height: 400px; border: 1px solid #ccc; border-radius: 5px;"
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
        <!-- 教师修改提醒 -->
        <div v-if="tchange" style="margin-top: 10px; color: #e6a23c;">
          📢 教师已更新你的评分，请查看最新结果。
        </div>
      </el-card>
    </el-col>
  </el-row>

  <!-- 结果弹窗（只读分数） -->
  <el-dialog
    v-model="showResultDialog"
    title="📊 评测结果"
    width="70%"
    :close-on-click-modal="false"
    destroy-on-close
    @closed="onDialogClosed"
  >
    <ResultDisplayStudent :result="result" />
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, watch, computed, onBeforeUnmount } from 'vue'
import { useRoute } from 'vue-router'
import MonacoEditor from '@guolao/vue-monaco-editor'
import { getProblem, submitCode, getSubmission, markRead } from '../api'
import ResultDisplayStudent from '../components/ResultDisplayStudent.vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
marked.setOptions({
  gfm: true,
  breaks: true
})
const route = useRoute()
const user = JSON.parse(localStorage.getItem('user') || '{}')
const studentId = user.id

const problem = ref({})
const code = ref('')
const loading = ref(true)
const submitting = ref(false)
const result = ref(null)
const showResultDialog = ref(false)
const tchange = ref(false)

const editorOptions = {
  automaticLayout: true,
  fontSize: 14,
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
}

const formattedDescription = computed(() => {
  if (!problem.value.description) return ''
  return marked(problem.value.description, { breaks: true })
})

let active = true  // 用于避免组件卸载后更新状态

const loadData = async () => {
  const problemId = route.params.id
  if (!problemId) return
  loading.value = true
  try {
    const [probRes, subRes] = await Promise.all([
      getProblem(problemId),
      getSubmission(problemId, studentId)
    ])
    if (!active) return  // 组件已卸载，不更新
    problem.value = probRes.data
    if (subRes.data) {
      code.value = subRes.data.code
      result.value = {
        scores: subRes.data.scores,
        feedback: subRes.data.feedback,
        test_results: null
      }
      tchange.value = subRes.data.tchange
    } else {
      code.value = '# 请在这里编写你的代码\n'
      result.value = null
      tchange.value = false
    }
  } catch (err) {
    console.error('加载失败', err)
    if (active) ElMessage.error('加载题目失败')
  } finally {
    if (active) loading.value = false
  }
}

// 初始加载
onMounted(() => {
  active = true
  loadData()
})

// 组件销毁前取消标志
onBeforeUnmount(() => {
  active = false
})

// 监听路由参数变化，重新加载
watch(() => route.params.id, () => {
  loadData()
})

const handleSubmit = async () => {
  submitting.value = true
  try {
    const res = await submitCode(route.params.id, code.value, studentId)
    result.value = res.data
    tchange.value = false
    ElMessage.success('评测完成，点击“查看结果”查看详情')
  } catch (err) {
    console.error('提交失败', err)
    ElMessage.error('提交失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const onDialogClosed = async () => {
  if (tchange.value) {
    try {
      await markRead(route.params.id, studentId)
      tchange.value = false
    } catch (err) {
      console.error('清除标记失败', err)
    }
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
.description :deep(h1),
.description :deep(h2),
.description :deep(h3) {
  margin-top: 0;
}
.description :deep(p) {
  margin: 0 0 10px;
}
.description :deep(ul),
.description :deep(ol) {
  padding-left: 20px;
  margin: 5px 0;
}
.description :deep(strong) {
  font-weight: bold;
  color: #409eff;
}
.description :deep(code) {
  background: #f4f4f4;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}
</style>