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
      <pre style="background:#f5f5f5; padding:10px; overflow:auto;">{{ currentStudent.code }}</pre>
      <h4>评分修改</h4>
      <el-form :model="editScores" label-width="80px">
        <el-form-item label="正确性">
          <el-input-number v-model="editScores.correctness" :min="0" :max="50" />
        </el-form-item>
        <el-form-item label="规范性">
          <el-input-number v-model="editScores.normativity" :min="0" :max="20" />
        </el-form-item>
        <el-form-item label="效率">
          <el-input-number v-model="editScores.efficiency" :min="0" :max="20" />
        </el-form-item>
        <el-form-item label="可读性">
          <el-input-number v-model="editScores.readability" :min="0" :max="10" />
        </el-form-item>
        <el-form-item label="总分">
          <span>{{ computedTotal }}</span>
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="editFeedback" type="textarea" rows="6" />
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

const formattedDescription = computed(() => problem.value.description?.replace(/\n/g, '<br>') || '')

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
    // 刷新列表
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

// 监听路由变化重新加载
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
</style>