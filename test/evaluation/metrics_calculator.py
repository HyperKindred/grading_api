import re
from typing import Dict

def calculate_objective_metrics(feedback_text: str) -> Dict:
    """
    计算客观指标：反馈长度、结构、关键词覆盖率等
    
    Args:
        feedback_text: 模型反馈文本
        
    Returns:
        包含各项指标得分的字典
    """
    if not feedback_text or not isinstance(feedback_text, str):
        return {"error": "无效的反馈文本", "overall_score": 0}
    
    metrics = {
        "length_score": 0,
        "structure_score": 0,
        "keyword_coverage": 0,
        "overall_score": 0
    }
    
    try:
        # 1. 长度得分 (0-40分)
        text_length = len(feedback_text)
        if text_length < 100:
            length_score = 10  # 太短
        elif text_length < 300:
            length_score = 20  # 较短
        elif text_length < 800:
            length_score = 30  # 适中
        elif text_length < 2000:
            length_score = 40  # 详细
        else:
            length_score = 35  # 可能过于冗长
        
        metrics["length_score"] = length_score
        metrics["text_length"] = text_length
        
        # 2. 结构得分 (0-30分)
        # 检查是否有结构化的反馈元素
        structure_elements = 0
        structure_keywords = [
            r"问题[：:].*", r"原因[：:].*", r"建议[：:].*",
            r"优化[：:].*", r"总结[：:].*", r"改进[：:].*",
            r"1\..*", r"2\..*", r"3\..*",  # 编号列表
            r"[-*•].*",  # 项目符号
            r"```.*```",  # 代码块
        ]
        
        for pattern in structure_keywords:
            if re.search(pattern, feedback_text, re.MULTILINE | re.DOTALL):
                structure_elements += 1
        
        # 根据结构元素数量评分
        if structure_elements >= 4:
            structure_score = 30
        elif structure_elements >= 3:
            structure_score = 25
        elif structure_elements >= 2:
            structure_score = 20
        elif structure_elements >= 1:
            structure_score = 15
        else:
            structure_score = 10
        
        metrics["structure_score"] = structure_score
        metrics["structure_elements"] = structure_elements
        
        # 3. 关键词覆盖率 (0-30分)
        # 编程反馈的关键词
        programming_keywords = [
            "时间复杂度", "空间复杂度", "优化", "算法", "循环",
            "条件", "变量", "函数", "参数", "返回值",
            "错误", "异常", "测试", "用例", "边界",
            "效率", "性能", "内存", "递归", "迭代",
            "哈希表", "数组", "字符串", "列表", "字典"
        ]
        
        found_keywords = []
        for keyword in programming_keywords:
            if keyword in feedback_text:
                found_keywords.append(keyword)
        
        keyword_coverage = len(found_keywords) / len(programming_keywords) * 30
        metrics["keyword_coverage"] = round(min(keyword_coverage, 30), 2)
        metrics["found_keywords"] = found_keywords
        metrics["total_keywords"] = len(programming_keywords)
        
        # 4. 计算总分 (0-100分)
        overall_score = length_score + structure_score + keyword_coverage
        metrics["overall_score"] = round(min(overall_score, 100), 2)
        
        # 5. 添加其他有用指标
        metrics["has_code_block"] = 1 if "```" in feedback_text else 0
        metrics["has_suggestions"] = 1 if any(word in feedback_text for word in ["建议", "可以", "应该", "改进"]) else 0
        metrics["has_explanation"] = 1 if any(word in feedback_text for word in ["因为", "原因", "因此", "所以"]) else 0
        
    except Exception as e:
        metrics["error"] = f"计算指标时出错: {str(e)}"
        metrics["overall_score"] = 0
    
    return metrics


# 测试函数
def test_metrics_calculator():
    """测试客观指标计算"""
    test_feedback = """
问题：你的代码时间复杂度较高
原因：使用了双重循环，时间复杂度为O(n²)
建议：可以使用哈希表优化到O(n)

优化示例：
```python
def twoSum(nums, target):
    hash_map = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in hash_map:
            return [hash_map[complement], i]
        hash_map[num] = i
    return []
    总结：代码逻辑正确但效率有待提升。
"""
    result = calculate_objective_metrics(test_feedback)
    print("测试客观指标计算:")
    for key, value in result.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value}")
        elif isinstance(value, list):
            print(f"  {key}: {len(value)} 个")
        else:
            print(f"  {key}: {value}")
            
if __name__ == "__main__":
    test_metrics_calculator()