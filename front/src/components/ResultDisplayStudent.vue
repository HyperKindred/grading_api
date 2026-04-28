<template>
  <div class="result-display" v-if="result">
    <h3>📊 评测结果</h3>

    <div v-if="result.scores" class="scores">
      <div class="score-item">
        <span class="score-label">正确性</span>
        <span class="score-value">{{ result.scores.correctness }}</span>
        <span class="score-max">/ 50</span>
      </div>
      <div class="score-item">
        <span class="score-label">规范性</span>
        <span class="score-value">{{ result.scores.normativity }}</span>
        <span class="score-max">/ 20</span>
      </div>
      <div class="score-item">
        <span class="score-label">效率</span>
        <span class="score-value">{{ result.scores.efficiency }}</span>
        <span class="score-max">/ 20</span>
      </div>
      <div class="score-item">
        <span class="score-label">可读性</span>
        <span class="score-value">{{ result.scores.readability }}</span>
        <span class="score-max">/ 10</span>
      </div>
      <div class="score-item total">
        <span class="score-label">总分</span>
        <span class="score-value">{{ result.scores.total }}</span>
        <span class="score-max">/ 100</span>
      </div>
    </div>

    <div v-if="result.feedback" class="ai-feedback">
      <h4>🤖 AI 综合反馈</h4>
      <div class="feedback-content" v-html="renderedFeedback"></div>
    </div>

    <!-- 测试输出部分省略，可按需保留 -->
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { marked } from 'marked'

const props = defineProps(['result'])

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
}
.score-value {
  font-size: 1.3em;
  font-weight: bold;
  color: #2e7d5e;
}
.score-max {
  color: #7f8c8d;
  font-size: 0.9em;
}
.total {
  grid-column: span 2;
  border-top: 1px dashed #4caf50;
  padding-top: 10px;
}
.ai-feedback {
  background: #f0f7ff;
  border-left: 4px solid #409eff;
  padding: 12px 16px;
  margin: 20px 0;
  border-radius: 8px;
}
.feedback-content {
  line-height: 1.6;
  font-size: 0.95em;
}
</style>