import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 假设你有一个可以调用多模型的函数
from llm_client import get_llm_feedback_with_model
from evaluation.evaluator import ModelEvaluator

def get_llm_feedback_with_model(code: str, test_results: str, model_name: str) -> str:
    """
    模拟函数 - 你需要根据实际实现修改
    这里简化处理，直接返回示例文本
    """
    # 在实际应用中，这里应该调用真实的OpenRouter API
    return f"这是模型 {model_name} 对代码的反馈示例。学生代码使用了减法而不是加法。"

def main():
    """主函数：执行多模型对比评估"""
    
    # 准备测试样本
    samples = [
        {
            "id": "sample_1",
            "code": """def add(a, b):
    return a - b  # 故意写错成减法""",
            "test_results": "测试失败：2 + 3 期望得到 5，实际得到 -1",
            "question": "实现两个数字的加法函数 add(a, b)"
        }
    ]
    
    # 选择要对比的模型
    models_to_compare = [
        "openai/gpt-4o",
        "deepseek/deepseek-chat", 
        "qwen/qwen-plus"
    ]
    
    # 初始化评估器
    evaluator = ModelEvaluator()
    
    # 对每个样本执行评估
    for sample in samples:
        print(f"\n{'='*60}")
        print(f"处理样本: {sample['id']}")
        print(f"{'='*60}")
        
        # 获取各模型的反馈
        model_feedbacks = {}
        for model_name in models_to_compare:
            print(f"  正在获取 {model_name} 的反馈...")
            feedback = get_llm_feedback_with_model(
                sample["code"], 
                sample["test_results"], 
                model_name
            )
            model_feedbacks[model_name] = feedback
        
        # 执行完整评估
        result = evaluator.run_complete_evaluation(
            sample_id=sample["id"],
            student_code=sample["code"],
            test_results=sample["test_results"],
            model_feedbacks=model_feedbacks,
            question_description=sample["question"]
        )
        
        print(f"评估完成！最佳模型: {result['summary']['top_model']}")
    
    print(f"\n所有评估完成！结果保存在: {evaluator.output_dir}/")

if __name__ == "__main__":
    main()