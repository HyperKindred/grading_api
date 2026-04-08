import json
import glob
from collections import defaultdict

def prepare_evaluation_data(summary_report_path):
    """
    从 summary_report.json 自动构建数据集索引，用于定位所有详细结果文件。
    这是运行 calculate_comprehensive_scores 函数前的必要步骤。
    """
    with open(summary_report_path, 'r', encoding='utf-8') as f:
        summary_data = json.load(f)

    # 构建一个包含所有样本详细文件路径的列表
    sample_details = []
    for sample in summary_data['samples']:
        # 根据你的文件命名规则构造详细文件名
        detail_filename = f"eval_{sample['sample_id']}.json"
        detail_filepath = f"evaluation_results/{detail_filename}" # 请根据你的实际目录调整
        sample_details.append({
            'sample_id': sample['sample_id'],
            'detail_file': detail_filepath
        })

    # 这个结构就是可以传递给计算函数的 your_evaluation_data
    evaluation_data_for_calc = {
        'samples': sample_details,
        'total_samples': len(sample_details)
    }
    return evaluation_data_for_calc

def calculate_comprehensive_scores(evaluation_data, obj_weight=0.7, expert_weight=0.3):
    """
    使用详细文件计算综合得分 (核心函数)
    evaluation_data 参数就是 prepare_evaluation_data 函数的返回结果。
    """
    model_stats = defaultdict(lambda: {'objective_scores': [], 'expert_similarities': []})

    for sample_info in evaluation_data['samples']:
        detail_file_path = sample_info['detail_file']
        try:
            with open(detail_file_path, 'r', encoding='utf-8') as f:
                detail_result = json.load(f)
        except FileNotFoundError:
            print(f"警告: 未找到文件 {detail_file_path}，跳过样本 {sample_info['sample_id']}")
            continue

        # 1. 收集客观指标分
        if 'objective_metrics' in detail_result:
            for model_name, metrics in detail_result['objective_metrics'].items():
                if isinstance(metrics, dict) and 'overall_score' in metrics:
                    model_stats[model_name]['objective_scores'].append(metrics['overall_score'])
                # 处理可能的错误字段
                elif metrics and 'error' not in str(metrics):
                    print(f"样本 {sample_info['sample_id']} 中模型 {model_name} 的客观指标格式异常: {metrics}")

        # 2. 收集专家相似度分
        if 'expert_similarities' in detail_result:
            for model_name, similarity in detail_result['expert_similarities'].items():
                if isinstance(similarity, (int, float)):
                    model_stats[model_name]['expert_similarities'].append(similarity)

    # 3. 计算每个模型的平均值和综合得分
    comprehensive_scores = []
    for model_name, stats in model_stats.items():
        if stats['objective_scores'] and stats['expert_similarities']:
            avg_obj = sum(stats['objective_scores']) / len(stats['objective_scores'])
            avg_exp = sum(stats['expert_similarities']) / len(stats['expert_similarities'])

            # 计算综合得分（将专家相似度放大100倍以匹配客观分量级）
            comprehensive_score = (avg_obj * obj_weight) + (avg_exp * 100 * expert_weight)

            comprehensive_scores.append({
                'model': model_name,
                'avg_objective_score': round(avg_obj, 2),
                'avg_expert_similarity': round(avg_exp, 4),
                'comprehensive_score': round(comprehensive_score, 2),
                'samples_count_obj': len(stats['objective_scores']), # 用于校验数据完整性
                'samples_count_exp': len(stats['expert_similarities'])
            })

    # 4. 按综合得分排序
    comprehensive_scores.sort(key=lambda x: x['comprehensive_score'], reverse=True)
    return comprehensive_scores

# ====== 使用示例 ======
if __name__ == "__main__":
    # 步骤 1: 准备数据（替换为你的实际路径）
    summary_path = "evaluation_results/summary_report.json" 
    evaluation_data = prepare_evaluation_data(summary_path)
    print("数据准备完成，共找到", evaluation_data['total_samples'], "个样本的索引。")

    # 步骤 2: 计算综合得分
    final_scores = calculate_comprehensive_scores(evaluation_data)

    # 步骤 3: 打印漂亮的报告
    print("\n" + "="*65)
    print("模型综合评估报告 (基于详细结果文件计算)")
    print("="*65)
    print(f"{'排名':<6} {'模型名称':<25} {'客观均分':<10} {'专家相似度':<12} {'综合得分':<10}")
    print("-"*65)

    for i, result in enumerate(final_scores, 1):
        # 检查数据是否完整（可选）
        data_flag = ""
        if result['samples_count_obj'] != evaluation_data['total_samples']:
            data_flag += f"(客观分样本数:{result['samples_count_obj']}) "
        if result['samples_count_exp'] != evaluation_data['total_samples']:
            data_flag += f"(相似度样本数:{result['samples_count_exp']})"

        print(f"{i:<6} {result['model']:<25} {result['avg_objective_score']:<10.2f} "
              f"{result['avg_expert_similarity']:<12.4f} {result['comprehensive_score']:<10.2f} {data_flag}")