# 三层评估主类
import os
import json
from datetime import datetime
from typing import Dict
from .metrics_calculator import calculate_objective_metrics
from .llm_judge import evaluate_with_llm_judge

class ModelEvaluator:
    """三层评估主类"""
    
    def __init__(self, output_dir: str = "evaluation_results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def run_complete_evaluation(
        self,
        sample_id: str,
        student_code: str,
        test_results: str,
        model_feedbacks: Dict[str, str],
        question_description: str = "",
        expert_feedback_path: str = None
    ) -> Dict:
        """
        执行完整的三层评估
        """
        
        # 构建评估上下文（纯文本格式）
        context = f"""
题目描述
{question_description}

学生代码
```python
{student_code}

测试结果
{test_results}
"""
        # 第一层：客观指标
        print(f"[{sample_id}] 计算客观指标...")
        objective_results = {}
        for model_name, feedback in model_feedbacks.items():
            objective_results[model_name] = calculate_objective_metrics(feedback)
        
        # 第二层：LLM裁判评估
        print(f"[{sample_id}] 进行LLM裁判评估...")
        llm_evaluation = evaluate_with_llm_judge(model_feedbacks, context)

        # 第三层：与专家反馈的相似度（如果有专家反馈文件）
        expert_similarities = {}
        if expert_feedback_path and os.path.exists(expert_feedback_path):
            print(f"[{sample_id}] 计算与专家反馈的相似度...")
            try:
                with open(expert_feedback_path, 'r', encoding='utf-8') as f:
                    expert_feedback = f.read()
                
                # 为每个模型计算相似度
                for model_name, feedback in model_feedbacks.items():
                    similarity = self.calculate_vs_expert_similarity(feedback, expert_feedback)
                    expert_similarities[model_name] = similarity
            except Exception as e:
                print(f"[{sample_id}] 读取专家反馈失败: {e}")
                expert_similarities = {"error": str(e)}
        else:
            expert_similarities = {"note": "未提供专家反馈文件"}
    
        # 整合结果
        final_result = {
            "sample_id": sample_id,
            "context": {
                "student_code": student_code,
                "test_results": test_results[:500] + "..." if len(test_results) > 500 else test_results,
                "question_description": question_description[:200] + "..." if len(question_description) > 200 else question_description
            },
            "model_feedbacks": {k: v[:300] + "..." if len(v) > 300 else v for k, v in model_feedbacks.items()},
            "objective_metrics": objective_results,
            "llm_evaluation": llm_evaluation,
            "expert_similarities": expert_similarities,
            "summary": self.generate_summary(objective_results, llm_evaluation, expert_similarities),
    }
        
        # 保存结果
        self.save_results(sample_id, final_result)
        
        return final_result

    def generate_summary(self, objective_metrics, llm_evaluation, expert_similarities=None):
        """生成评估摘要"""
        summary = {
            "model_count": len(objective_metrics),
            "evaluation_status": "完成"
        }
        
        # 从LLM裁判评估获取排名
        if "error" not in llm_evaluation:
            ranking = llm_evaluation.get("ranking", [])
            if ranking:
                summary["llm_judge_top_model"] = ranking[0]
                summary["llm_judge_ranking"] = ranking
        
        # 从客观指标获取最佳模型
        best_objective_model = None
        best_objective_score = -1
        for model_name, metrics in objective_metrics.items():
            if "error" not in metrics:
                score = metrics.get("overall_score", 0)
                if score > best_objective_score:
                    best_objective_score = score
                    best_objective_model = model_name
        
        if best_objective_model:
            summary["objective_top_model"] = best_objective_model
            summary["objective_top_score"] = best_objective_score
        
        # 从专家相似度获取最佳模型
        if expert_similarities and "error" not in expert_similarities and "note" not in expert_similarities:
            best_expert_model = None
            best_expert_similarity = -1
            for model_name, similarity in expert_similarities.items():
                if similarity > best_expert_similarity:
                    best_expert_similarity = similarity
                    best_expert_model = model_name
            
            if best_expert_model:
                summary["expert_top_model"] = best_expert_model
                summary["expert_top_similarity"] = best_expert_similarity
        
        # 综合推荐（简单策略：优先考虑LLM裁判，其次是客观指标）
        if "llm_judge_top_model" in summary:
            summary["recommended_model"] = summary["llm_judge_top_model"]
        elif "objective_top_model" in summary:
            summary["recommended_model"] = summary["objective_top_model"]
        else:
            summary["recommended_model"] = "无法确定"
        
        return summary

    def save_results(self, sample_id: str, results: Dict):
        """保存评估结果到文件"""
        filename = f"{self.output_dir}/eval_{sample_id}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"评估结果已保存到: {filename}")
        
        # 同时更新摘要报告
        self.update_summary_report(results)

    def update_summary_report(self, result: Dict):
        """更新汇总报告"""
        summary_file = f"{self.output_dir}/summary_report.json"
        
        summary_data = {}
        if os.path.exists(summary_file):
            try:
                with open(summary_file, 'r', encoding='utf-8') as f:
                    summary_data = json.load(f)
            except:
                summary_data = {}
        
        # 确保结构存在
        if "samples" not in summary_data:
            summary_data["samples"] = []
        
        # 添加新样本摘要
        sample_summary = {
            "sample_id": result["sample_id"],
            "summary": result.get("summary", {}),
            "model_count": len(result.get("model_feedbacks", {}))
        }
        
        # 检查是否已存在该样本
        existing_idx = -1
        for i, sample in enumerate(summary_data["samples"]):
            if sample["sample_id"] == result["sample_id"]:
                existing_idx = i
                break
        
        if existing_idx >= 0:
            summary_data["samples"][existing_idx] = sample_summary
        else:
            summary_data["samples"].append(sample_summary)
        
        # 更新统计信息
        summary_data["total_samples"] = len(summary_data["samples"])
        summary_data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary_data, f, ensure_ascii=False, indent=2)

    def calculate_vs_expert_similarity(self, llm_feedback: str, expert_feedback: str) -> float:
        """
        计算模型反馈与专家反馈的相似度
        
        Args:
            llm_feedback: 模型反馈文本
            expert_feedback: 专家反馈文本
            
        Returns:
            相似度分数 (0-1)
        """
        if not expert_feedback or not llm_feedback:
            return 0.0
        
        # 方法1：简单的关键词重叠率
        import re
        
        # 清理文本：去除标点，转为小写，分词
        def clean_text(text):
            # 去除标点符号
            text = re.sub(r'[^\w\s]', ' ', text)
            # 转为小写
            text = text.lower()
            # 分割单词
            words = text.split()
            # 去除停用词（简单版本）
            stop_words = {'的', '了', '在', '是', '和', '有', '这', '那', '就', '都', '而', '及', '与', '或'}
            words = [w for w in words if w not in stop_words]
            return set(words)
        
        llm_words = clean_text(llm_feedback)
        expert_words = clean_text(expert_feedback)
        
        if not expert_words:
            return 0.0
        
        # 计算Jaccard相似度
        intersection = len(llm_words.intersection(expert_words))
        union = len(llm_words.union(expert_words))
        
        if union == 0:
            return 0.0
        
        similarity = intersection / union
        
        return round(similarity, 4)