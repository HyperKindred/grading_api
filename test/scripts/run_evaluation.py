import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llm_client import get_llm_feedback_with_model
from evaluation.evaluator import ModelEvaluator
from grader import CodeGrader  # 使用新的CodeGrader类

def main():
    # 1. 加载数据集
    dataset_path = 'dataset/dataset_index.json'
    print(f"[INFO] 加载数据集: {dataset_path}")
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(dataset_path, 'r', encoding='utf-8') as f:
        dataset = json.load(f)
    
    # 2. 初始化评估器和代码执行器
    evaluator = ModelEvaluator(output_dir="evaluation_results")
    grader = CodeGrader()
    
    # 3. 选择要对比的模型
    models_to_compare = [
        "openai/gpt-4o",
        "deepseek/deepseek-chat", 
        "qwen/qwen-plus",
        "anthropic/claude-3-5-sonnet",  
        "google/gemini-2.5-pro",       
        "z-ai/glm-4.7",              
        "minimax/minimax-m2.1",                
        "meta-llama/llama-3.3-70b-instruct",           
    ]
    
    # 4. 遍历样本
    samples = dataset['samples']
    total_samples = len(samples)
    print(f"[INFO] 共 {total_samples} 个样本")
    
    for i, sample in enumerate(samples):
        print(f"\n{'='*60}")
        print(f"处理样本 {i+1}/{total_samples}: {sample['id']}")
        print(f"类型: {sample['category']}, 难度: {sample['difficulty']}")
        print(f"{'='*60}")
        
        try:
            # 4.1 读取学生错误代码
            student_code_path = sample.get('student_code_path', '')
            if not student_code_path:
                print(f"  ⚠️  跳过：未找到学生代码路径")
                continue

            # 修正路径：转换为基于项目根目录的绝对路径
            if not os.path.isabs(student_code_path):
                student_code_path = os.path.join(project_root, 'dataset', student_code_path)
                
            print(f"  学生代码路径: {student_code_path}")
            if not os.path.exists(student_code_path):
                print(f"  ❌ 错误：文件不存在: {student_code_path}")
                continue
                
            with open(student_code_path, 'r', encoding='utf-8') as f:
                student_code = f.read()
            print(f"  学生代码长度: {len(student_code)} 字符")
            
            # 4.2 读取测试用例
            test_cases_path = sample.get('test_cases_path', '')
            if not test_cases_path:
                print(f"  ⚠️  警告：未找到测试用例文件，使用模拟结果")
                test_cases = None
            else:
                # 修正路径
                if not os.path.isabs(test_cases_path):
                    test_cases_path = os.path.join(project_root, 'dataset', test_cases_path)
                
                print(f"  测试用例文件: {test_cases_path}")
                if not os.path.exists(test_cases_path):
                    print(f"  ❌ 警告：测试用例文件不存在，使用模拟结果")
                    test_cases = None
                else:
                    with open(test_cases_path, 'r', encoding='utf-8') as f:
                        test_cases = f.read()
                    print(f"  测试用例长度: {len(test_cases)} 字符")

            # 4.3 读取参考解决方案（如果需要）
            reference_solution = ""
            reference_solution_path = sample.get('reference_solution_path', '')
            if reference_solution_path:
                # 修正路径
                if not os.path.isabs(reference_solution_path):
                    reference_solution_path = os.path.join(project_root, 'dataset', reference_solution_path)
                
                if os.path.exists(reference_solution_path):
                    with open(reference_solution_path, 'r', encoding='utf-8') as f:
                        reference_solution = f.read()
                    print(f"  参考解决方案: {reference_solution_path} ({len(reference_solution)} 字符)")
                else:
                    print(f"  ⚠️  警告：参考解决方案文件不存在: {reference_solution_path}")
            
            # 4.4 运行真实测试（如果有测试用例）
            if test_cases:
                print(f"  运行真实测试...")
                
                # 构建样本数据（多文件支持）
                sample_data = {
                    'student_code': student_code,
                    'test_cases': test_cases,
                    'sample_id': sample['id']
                }
                
                # 如果测试用例需要参考解决方案，就添加进去
                if reference_solution:
                    sample_data['reference_solution'] = reference_solution
                
                # 运行测试
                test_results = grader.run_tests_for_dataset_sample(sample_data)
                
                # 分析测试结果
                analysis = grader.analyze_test_results(test_results)
                print(f"    测试分析: {analysis['summary']}")
                
                # 如果测试完全失败，考虑使用模拟结果
                if analysis['passed'] == 0 and analysis['total_tests'] > 0:
                    print(f"    ⚠️  所有测试都失败了，但仍使用真实测试结果继续")
            else:
                # 生成智能模拟结果
                test_results = generate_mock_test_result(
                    student_code, 
                    sample['problem_description'],
                    sample['category']
                )
                print(f"  使用模拟测试结果")
            
            print(f"  测试结果长度: {len(test_results)} 字符")
            
            # 4.5 获取各模型的反馈
            model_feedbacks = {}
            for model_name in models_to_compare:
                model_short_name = model_name.split('/')[-1]
                print(f"  正在获取 {model_short_name} 的反馈...")
                try:
                    feedback = get_llm_feedback_with_model(
                        student_code,
                        test_results,
                        model_name
                    )
                    model_feedbacks[model_name] = feedback
                    print(f"    ✓ 成功 (长度: {len(feedback)} 字符)")
                except Exception as e:
                    error_msg = str(e)[:100]
                    print(f"    ✗ 失败: {error_msg}")
                    model_feedbacks[model_name] = f"获取反馈失败: {error_msg}"
            
            # 4.6 执行三层评估
            print(f"  开始三层评估...")
            
            # 构建专家反馈路径
            expert_feedback_path = None
            if sample.get('expert_feedback_path'):
                expert_feedback_path = sample['expert_feedback_path']
                if not os.path.isabs(expert_feedback_path):
                    expert_feedback_path = os.path.join(project_root, 'dataset', expert_feedback_path)
            print(f"  专家反馈路径: {expert_feedback_path}")
            print(f"  专家文件存在: {os.path.exists(expert_feedback_path)}")
            
            if os.path.exists(expert_feedback_path):
                with open(expert_feedback_path, 'r', encoding='utf-8') as f:
                    expert_content = f.read()
                print(f"  专家反馈长度: {len(expert_content)} 字符")
            result = evaluator.run_complete_evaluation(
                sample_id=sample['id'],
                student_code=student_code,
                test_results=test_results,
                model_feedbacks=model_feedbacks,
                question_description=sample.get('problem_description', ''),
                expert_feedback_path=expert_feedback_path
            )
            
            # 4.7 打印本次结果摘要
            summary = result.get('summary', {})
            
            # 尝试多个可能的字段名获取最佳模型
            top_model = (summary.get('recommended_model') or 
                        summary.get('top_model') or 
                        summary.get('llm_judge_top_model') or 
                        summary.get('objective_top_model') or 
                        'N/A')
            
            # 获取综合得分
            top_score = (summary.get('objective_top_score') or 
                        summary.get('top_score') or 
                        summary.get('expert_top_similarity') or 
                        0)
            
            print(f"  ✅ 评估完成！")
            print(f"     最佳模型: {top_model}")
            print(f"     综合得分: {top_score:.2f}/100")
            
            # 显示各模型得分
            if 'objective_metrics' in result:
                print("     客观指标得分:")
                for model, metrics in result['objective_metrics'].items():
                    if 'error' not in metrics:
                        model_short = model.split('/')[-1]
                        score = metrics.get('overall_score', 0)
                        print(f"       - {model_short}: {score:.2f}")
            
            if 'expert_similarities' in result:
                print("     专家相似度:")
                for model, similarity in result['expert_similarities'].items():
                    if isinstance(similarity, (int, float)):
                        model_short = model.split('/')[-1]
                        print(f"       - {model_short}: {similarity:.4f}")
            
        except Exception as e:
            print(f"  ❌ 处理样本 {sample['id']} 时出错: {str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*60}")
    print(f"批量评估完成！")
    print(f"详细结果保存在: evaluation_results/")
    print(f"建议查看以下文件:")
    print(f"  - evaluation_results/summary_report.json (汇总报告)")
    print(f"  - evaluation_results/detailed_results/ (详细结果)")
    print(f"{'='*60}")

def generate_mock_test_result(student_code, problem_description, category):
    """根据代码和问题类型生成智能模拟测试结果"""
    
    # 根据错误类别生成不同的测试结果
    if category == "inefficiency":
        mock_result = f"""
题目: {problem_description[:100]}...

模拟测试报告
============

🔍 代码分析:
- 语法检查: 通过 ✓
- 导入检查: 通过 ✓

🧪 功能测试结果:
1. 基础用例测试 (5个):
   ✓ 用例 [2,7,11,15], 目标 9: 通过 (结果: [0,1])
   ✓ 用例 [3,2,4], 目标 6: 通过 (结果: [1,2])
   ✓ 用例 [3,3], 目标 6: 通过 (结果: [0,1])
   ✓ 用例 [0,4,3,0], 目标 0: 通过 (结果: [0,3])
   ✓ 用例 [-1,-2,-3,-4,-5], 目标 -8: 通过 (结果: [2,4])

2. 边界测试 (3个):
   ✓ 空数组 []: 通过 (结果: [])
   ✓ 无解情况 [1,2,3], 目标 10: 通过 (结果: [])
   ✓ 单个元素 [5], 目标 5: 通过 (结果: [])

⏱️ 性能测试结果:
3. 小规模性能测试 (100个元素):
   ✓ 通过，耗时 0.002秒

4. 中规模性能测试 (1000个元素):
   ⚠️ 通过但较慢，耗时 0.152秒 (接近超时)

5. 大规模性能测试 (5000个元素):
   ❌ 超时失败 (限制: 2秒，实际: >5秒)

📊 性能分析:
- 时间复杂度: O(n²) (双重循环)
- 空间复杂度: O(1)
- 问题: 算法在数据规模增大时性能急剧下降

✅ 功能正确性: 10/10
⚠️ 代码效率: 3/10
🔧 建议优化: 使用哈希表将时间复杂度优化为O(n)

总结: 代码逻辑正确但效率低下，不适合处理大规模数据。
"""
    else:
        # 通用模拟结果
        mock_result = f"""
题目: {problem_description[:100]}...

模拟测试报告
============

🔍 代码分析:
- 语法检查: 通过 ✓
- 导入检查: 通过 ✓

🧪 功能测试结果:
1. 基础用例测试: 3/5 通过
2. 边界测试: 2/3 通过
3. 异常处理: 1/2 通过

📊 总体评估:
- 通过率: 60%
- 主要问题: 逻辑错误和边界条件处理不当

总结: 代码需要进一步调试和完善。
"""
    
    return mock_result

if __name__ == "__main__":
    main()