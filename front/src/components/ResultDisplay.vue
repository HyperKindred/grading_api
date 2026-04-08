<template>
  <div class="result-display" v-if="result">
    <h3>📊 评测结果</h3>

    <!-- 四维评分展示（已有） -->
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

    <!-- 新增：AI 综合反馈 -->
    <div v-if="result.feedback" class="ai-feedback">
      <h4>🤖 AI 综合反馈</h4>
      <div class="feedback-content" v-html="formattedFeedback"></div>
    </div>

    <!-- 原有测试输出部分 -->
    <div v-if="result.test_results.error" class="error">{{ result.test_results.error }}</div>
    <div v-else>
      <p>
        <strong>状态：</strong>
        <span :class="result.test_results.all_passed ? 'success' : 'fail'">
          {{ result.test_results.all_passed ? '✅ 全部通过' : '❌ 有未通过的测试' }}
        </span>
      </p>

      <details>
        <summary>📄 公开测试输出</summary>
        <pre>{{ result.test_results.public.output }}</pre>
      </details>
      <details v-if="result.test_results.hidden">
        <summary>🔒 隐藏测试输出</summary>
        <pre>{{ result.test_results.hidden.output }}</pre>
      </details>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps(['result'])

// 将反馈中的换行转换为 <br>，并保留空格格式
const formattedFeedback = computed(() => {
  if (!props.result?.feedback) return ''
  // 转义 HTML 防止注入，但保留换行和空格（用 white-space: pre-wrap 更安全）
  // 这里简单处理：将 \n 替换为 <br>
  return props.result.feedback.replace(/\n/g, '<br>')
})
</script>

<style scoped>
.result-display {
  margin-top: 30px;
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
  align-items: baseline;
}
.score-label {
  font-weight: bold;
  color: #2c3e50;
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

/* 新增样式：AI 反馈区域 */
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
  white-space: pre-wrap;    /* 保留换行和空格 */
  line-height: 1.6;
  font-size: 0.95em;
  color: #2c3e50;
}
</style>