<template>
  <div class="result-display" v-if="result">
    <h3>📊 评测结果</h3>

    <!-- 可编辑分数区域 -->
    <div v-if="editableScores" class="scores">
      <div class="score-item">
        <span class="score-label">正确性</span>
        <el-input-number
          v-model="editableScores.correctness"
          :min="0"
          :max="50"
          :step="1"
          size="small"
          controls-position="right"
        />
        <span class="score-max">/ 50</span>
      </div>
      <div class="score-item">
        <span class="score-label">规范性</span>
        <el-input-number
          v-model="editableScores.normativity"
          :min="0"
          :max="20"
          :step="1"
          size="small"
          controls-position="right"
        />
        <span class="score-max">/ 20</span>
      </div>
      <div class="score-item">
        <span class="score-label">效率</span>
        <el-input-number
          v-model="editableScores.efficiency"
          :min="0"
          :max="20"
          :step="1"
          size="small"
          controls-position="right"
        />
        <span class="score-max">/ 20</span>
      </div>
      <div class="score-item">
        <span class="score-label">可读性</span>
        <el-input-number
          v-model="editableScores.readability"
          :min="0"
          :max="10"
          :step="1"
          size="small"
          controls-position="right"
        />
        <span class="score-max">/ 10</span>
      </div>
      <div class="score-item total">
        <span class="score-label">总分</span>
        <span class="score-value">{{ computedTotal }}</span>
        <span class="score-max">/ 100</span>
      </div>
      <el-button size="small" type="primary" plain @click="resetScores">重置分数</el-button>
    </div>

    <!-- AI 综合反馈（Markdown 渲染） -->
    <div v-if="result.feedback" class="ai-feedback">
      <h4>🤖 AI 综合反馈</h4>
      <div class="feedback-content" v-html="renderedFeedback"></div>
    </div>

    <!-- 原有测试输出部分 -->
    <div v-if="result.test_results?.error" class="error">{{ result.test_results.error }}</div>
    <div v-else-if="result.test_results">
      <p>
        <strong>状态：</strong>
        <span :class="result.test_results.all_passed ? 'success' : 'fail'">
          {{ result.test_results.all_passed ? '✅ 全部通过' : '❌ 有未通过的测试' }}
        </span>
      </p>

      <details>
        <summary>📄 公开测试输出</summary>
        <pre>{{ result.test_results.public?.output || '无输出' }}</pre>
      </details>
      <details v-if="result.test_results.hidden">
        <summary>🔒 隐藏测试输出</summary>
        <pre>{{ result.test_results.hidden.output || '无输出' }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { marked } from 'marked'

const props = defineProps(['result'])

// 可编辑分数副本
const editableScores = ref(null)

// 监听 result 变化，初始化可编辑分数
watch(
  () => props.result,
  (newResult) => {
    if (newResult?.scores) {
      editableScores.value = { ...newResult.scores }
    }
  },
  { immediate: true, deep: true }
)

// 计算总分（基于可编辑分数）
const computedTotal = computed(() => {
  if (!editableScores.value) return 0
  const { correctness, normativity, efficiency, readability } = editableScores.value
  return (correctness || 0) + (normativity || 0) + (efficiency || 0) + (readability || 0)
})

// 重置为原始分数
const resetScores = () => {
  if (props.result?.scores) {
    editableScores.value = { ...props.result.scores }
  }
}

// 渲染 Markdown 反馈
const renderedFeedback = computed(() => {
  if (!props.result?.feedback) return ''
  return marked(props.result.feedback, { breaks: true })
})
</script>

<style scoped>
.result-display {
  margin-top: 10px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background: #fefefe;
}
.success { color: #4caf50; font-weight: bold; }
.fail { color: #f44336; font-weight: bold; }
pre {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 5px;
  overflow-x: auto;
  font-size: 0.9em;
}
.scores {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
  background: #e8f5e9;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 20px;
}
.score-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
.score-label {
  font-weight: bold;
  color: #2c3e50;
  min-width: 60px;
}
.score-value {
  font-size: 1.3em;
  font-weight: bold;
  color: #2e7d5e;
  margin: 0 5px;
}
.score-max {
  color: #7f8c8d;
  font-size: 0.9em;
}
.total {
  grid-column: span 2;
  border-top: 1px dashed #4caf50;
  padding-top: 10px;
  margin-top: 5px;
  font-size: 1.1em;
}
.total .score-value {
  font-size: 1.5em;
  color: #2c3e50;
}
.ai-feedback {
  background: #f0f7ff;
  border-left: 4px solid #409eff;
  padding: 12px 16px;
  margin: 20px 0;
  border-radius: 8px;
}
.ai-feedback h4 {
  margin: 0 0 10px 0;
  color: #409eff;
  font-size: 1.1em;
}
.feedback-content {
  line-height: 1.6;
  font-size: 0.95em;
  color: #2c3e50;
}
/* Markdown 内容样式 */
.feedback-content :deep(p) {
  margin: 0 0 10px;
}
.feedback-content :deep(ul), .feedback-content :deep(ol) {
  padding-left: 20px;
  margin: 5px 0;
}
.feedback-content :deep(strong) {
  font-weight: bold;
  color: #409eff;
}
.feedback-content :deep(code) {
  background: #f4f4f4;
  padding: 2px 4px;
  border-radius: 4px;
  font-family: monospace;
}
</style>