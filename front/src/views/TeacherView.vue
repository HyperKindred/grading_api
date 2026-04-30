<template>
  <el-row :gutter="20" style="height: 100%;">
    <!-- 左侧题目详情（可保留简短的题目描述） -->
    <el-col :span="10" style="height: 100%; overflow-y: auto;">
      <el-card v-if="!loadingProblem" style="height: 100%;">
        <template #header>
          <h2>{{ problem.title }}</h2>
        </template>
        <div class="description" v-html="formattedDescription"></div>
      </el-card>
      <el-skeleton v-else :rows="10" animated />
    </el-col>

    <!-- 右侧学生提交列表 -->
    <el-col :span="14" style="height: 100%; display: flex; flex-direction: column;">
      <el-card style="flex: 1; overflow-y: auto;">
        <template #header>
          <span>学生提交记录</span>
          <el-button type="primary" size="small" @click="refresh" style="margin-left: 10px;">刷新</el-button>
        </template>
        <el-table :data="submissions" stripe border style="width: 100%">
          <el-table-column prop="name" label="姓名" width="100" />
          <el-table-column prop="sid" label="学号" width="120" />
          <el-table-column label="正确性" width="80">
            <template #default="{ row }">{{ row.scores.correctness }}</template>
          </el-table-column>
          <el-table-column label="规范性" width="80">
            <template #default="{ row }">{{ row.scores.normativity }}</template>
          </el-table-column>
          <el-table-column label="效率" width="80">
            <template #default="{ row }">{{ row.scores.efficiency }}</template>
          </el-table-column>
          <el-table-column label="可读性" width="80">
            <template #default="{ row }">{{ row.scores.readability }}</template>
          </el-table-column>
          <el-table-column label="总分" width="80">
            <template #default="{ row }">{{ row.scores.total }}</template>
          </el-table-column>
          <el-table-column label="新提交" width="80">
            <template #default="{ row }">
              <el-tag v-if="row.schange" type="warning" size="small">新</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="100">
            <template #default="{ row }">
              <el-button type="primary" size="small" @click="showDetail(row)">详情</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </el-col>
  </el-row>

  <!-- 详情编辑弹窗 -->
  <el-dialog v-model="detailVisible" :title="`${currentStudent?.name} - 提交详情`" width="70%" destroy-on-close>
    <div v-if="currentStudent">
      <h4>学生代码</h4>
      <div class="code-viewer" v-html="highlightedCode"></div>

      <h4>评分修改</h4>
      <el-form :model="editScores" label-width="60px" label-position="left">
        <el-row :gutter="12">
          <el-col :span="6">
            <el-form-item label="正确性">
              <el-input-number v-model="editScores.correctness" :min="0" :max="50" controls-position="right"
                style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="规范性">
              <el-input-number v-model="editScores.normativity" :min="0" :max="20" controls-position="right"
                style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="效率">
              <el-input-number v-model="editScores.efficiency" :min="0" :max="20" controls-position="right"
                style="width: 100%;" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="可读性">
              <el-input-number v-model="editScores.readability" :min="0" :max="10" controls-position="right"
                style="width: 100%;" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="总分">
          <span style="font-weight: bold; font-size: 1.2em;">{{ computedTotal }}</span>
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="editFeedback" type="textarea" rows="10" placeholder="可在此编辑评语（支持Markdown）" />
        </el-form-item>
      </el-form>
    </div>
    <template #footer>
      <el-button @click="detailVisible = false">取消</el-button>
      <el-button type="primary" @click="saveChanges">保存修改</el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, watch, computed } from 'vue'
import { useRoute } from 'vue-router'
import { getProblem, getTeacherSubmissions, updateTeacherSubmission } from '../api'
import { ElMessage } from 'element-plus'
import hljs from 'highlight.js'
import 'highlight.js/styles/vs2015.css'
import { marked } from 'marked'
marked.setOptions({
  gfm: true,
  breaks: true
})
const route = useRoute()
const problemId = computed(() => route.params.id)

const problem = ref({})
const loadingProblem = ref(true)
const submissions = ref([])

const detailVisible = ref(false)
const currentStudent = ref(null)
const editScores = ref({})
const editFeedback = ref('')

const fetchProblem = async () => {
  if (!problemId.value) return
  loadingProblem.value = true
  try {
    const res = await getProblem(problemId.value)
    problem.value = res.data
  } catch (err) {
    console.error(err)
    ElMessage.error('加载题目失败')
  } finally {
    loadingProblem.value = false
  }
}

const fetchSubmissions = async () => {
  if (!problemId.value) return
  try {
    const res = await getTeacherSubmissions(problemId.value)
    submissions.value = res.data
  } catch (err) {
    console.error(err)
    ElMessage.error('加载学生提交列表失败')
  }
}

const refresh = () => {
  fetchSubmissions()
}

const formattedDescription = computed(() => {
  if (!problem.value.description) return ''
  return marked(problem.value.description, { breaks: true })
})

// 高亮代码（移除外层多余间距）
const highlightedCode = computed(() => {
  if (!currentStudent.value?.code) return ''
  const code = currentStudent.value.code
  const highlighted = hljs.highlight(code, { language: 'python' }).value
  return `<pre><code class="hljs language-python">${highlighted}</code></pre>`
})

// 计算总分
const computedTotal = computed(() => {
  if (!editScores.value) return 0
  const { correctness, normativity, efficiency, readability } = editScores.value
  return (correctness || 0) + (normativity || 0) + (efficiency || 0) + (readability || 0)
})

const showDetail = (student) => {
  currentStudent.value = student
  editScores.value = { ...student.scores }
  editFeedback.value = student.feedback || ''
  detailVisible.value = true
}

const saveChanges = async () => {
  if (!currentStudent.value) return
  try {
    await updateTeacherSubmission(
      problemId.value,
      currentStudent.value.student_id,
      editScores.value,
      editFeedback.value
    )
    ElMessage.success('保存成功')
    detailVisible.value = false
    await fetchSubmissions()
  } catch (err) {
    console.error(err)
    ElMessage.error('保存失败')
  }
}

onMounted(() => {
  fetchProblem()
  fetchSubmissions()
})

watch(problemId, () => {
  fetchProblem()
  fetchSubmissions()
})
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

/* 代码显示区域样式 - 优化内外边距和滚动 */
.code-viewer {
  background: #1e1e1e;
  border-radius: 8px;
  margin-bottom: 20px;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
}

.code-viewer pre {
  margin: 0;
  padding: 16px;
  font-family: 'Fira Code', 'Cascadia Code', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
  background: transparent;
  color: #d4d4d4;
  white-space: pre-wrap;
  word-break: break-word;
}

.code-viewer code {
  font-family: inherit;
}

/* 评分修改表单布局优化 */
.el-form .el-row {
  margin-bottom: 0;
}

.el-form-item {
  margin-bottom: 18px;
}

.el-form-item__label {
  padding-right: 4px !important;
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