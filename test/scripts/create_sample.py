import os
import json
import shutil
from pathlib import Path

def create_sample():
    """创建第二个样本：逻辑错误示例"""
    
    # 1. 设置目录
    project_root = Path(__file__).parent.parent
    sample_dir = project_root / "dataset" / "sample_06_style_issue"
    sample_dir.mkdir(exist_ok=True, parents=True)
    
    print(f"创建样本目录: {sample_dir}")
    
    # 2. 学生代码（代码风格问题：命名不规范、冗余代码）
    student_code = """def calc(lst):
    # 代码风格问题：函数名不清晰，变量名随意
    s = 0
    c = 0
    for x in lst:
        s = s + x
        c = c + 1
    if c == 0:
        return 0
    a = s / c
    return a

def FindPrimeNumbers(n):
    # 更多风格问题：不一致的命名，魔法数字，冗余注释
    primes = []
    for num in range(2, n+1):
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes
"""
    
    student_file = sample_dir / "student_code.py"
    student_file.write_text(student_code, encoding='utf-8')
    print(f"创建学生代码: {student_file}")
    
    # 3. 参考解决方案
    reference_solution = """def calculate_average(numbers: list[float]) -> float:
    '''计算数字列表的平均值
    
    Args:
        numbers: 数字列表
        
    Returns:
        平均值，如果列表为空则返回0.0
    '''
    if not numbers:
        return 0.0
    
    total = sum(numbers)
    count = len(numbers)
    return total / count

def find_prime_numbers(limit: int) -> list[int]:
    '''查找小于等于给定限制的所有质数
    
    Args:
        limit: 质数的上限
        
    Returns:
        质数列表
    '''
    if limit < 2:
        return []
    
    primes = []
    for num in range(2, limit + 1):
        # 优化：只需要检查到平方根
        is_prime = True
        for divisor in range(2, int(num ** 0.5) + 1):
            if num % divisor == 0:
                is_prime = False
                break
        
        if is_prime:
            primes.append(num)
    
    return primes

# 可选：使用更高效的筛法
def find_prime_numbers_sieve(limit: int) -> list[int]:
    '''使用埃拉托斯特尼筛法查找质数'''
    if limit < 2:
        return []
    
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    
    for i in range(2, int(limit ** 0.5) + 1):
        if is_prime[i]:
            for j in range(i * i, limit + 1, i):
                is_prime[j] = False
    
    return [i for i, prime in enumerate(is_prime) if prime]
"""
    
    reference_file = sample_dir / "reference_solution.py"
    reference_file.write_text(reference_solution, encoding='utf-8')
    print(f"创建参考方案: {reference_file}")
    
    # 4. 测试用例
    test_cases = """import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# 定义学生代码函数
def student_calculate_average(numbers):
    s = 0
    c = 0
    for x in numbers:
        s = s + x
        c = c + 1
    if c == 0:
        return 0
    a = s / c
    return a

def student_find_prime_numbers(n):
    primes = []
    for num in range(2, n+1):
        is_prime = True
        for i in range(2, num):
            if num % i == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

# 定义参考解决方案函数
def reference_calculate_average(numbers):
    if not numbers:
        return 0.0
    total = sum(numbers)
    count = len(numbers)
    return total / count

def reference_find_prime_numbers(limit):
    if limit < 2:
        return []
    
    primes = []
    for num in range(2, limit + 1):
        is_prime = True
        for divisor in range(2, int(num ** 0.5) + 1):
            if num % divisor == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(num)
    return primes

def test_calculate_average():
    '''测试平均值计算'''
    # 功能测试
    assert student_calculate_average([1, 2, 3, 4, 5]) == 3.0
    assert reference_calculate_average([1, 2, 3, 4, 5]) == 3.0
    
    # 边界测试
    assert student_calculate_average([]) == 0
    assert reference_calculate_average([]) == 0.0
    
    # 单元素测试
    assert student_calculate_average([5]) == 5.0
    assert reference_calculate_average([5]) == 5.0
    
    # 负数测试
    assert student_calculate_average([-1, -2, -3]) == -2.0
    assert reference_calculate_average([-1, -2, -3]) == -2.0

def test_find_prime_numbers():
    '''测试质数查找'''
    # 基本测试
    assert student_find_prime_numbers(10) == [2, 3, 5, 7]
    assert reference_find_prime_numbers(10) == [2, 3, 5, 7]
    
    # 边界测试
    assert student_find_prime_numbers(1) == []
    assert reference_find_prime_numbers(1) == []
    
    assert student_find_prime_numbers(2) == [2]
    assert reference_find_prime_numbers(2) == [2]
    
    # 性能相关（较小规模）
    primes_up_to_20 = [2, 3, 5, 7, 11, 13, 17, 19]
    assert student_find_prime_numbers(20) == primes_up_to_20
    assert reference_find_prime_numbers(20) == primes_up_to_20

def test_consistency():
    '''测试两个函数结果的一致性'''
    for n in range(1, 21):
        student_result = student_find_prime_numbers(n)
        reference_result = reference_find_prime_numbers(n)
        assert student_result == reference_result, f"n={n}时结果不一致"

def test_average_precision():
    '''测试平均值计算的精度'''
    numbers = [0.1, 0.2, 0.3]
    student_result = student_calculate_average(numbers)
    reference_result = reference_calculate_average(numbers)
    
    # 允许浮点数误差
    assert abs(student_result - 0.2) < 1e-10
    assert abs(reference_result - 0.2) < 1e-10

if __name__ == "__main__":
    test_calculate_average()
    test_find_prime_numbers()
    test_consistency()
    test_average_precision()
    print("所有功能测试通过！")
    print("注意：学生代码存在代码风格问题，但功能正确")
"""
    
    test_file = sample_dir / "test_cases.py"
    test_file.write_text(test_cases, encoding='utf-8')
    print(f"创建测试用例: {test_file}")
    
    # 5. 专家反馈
    expert_feedback = """## 诊断报告 (样本ID: sample_06_style_issue)

### 1. 核心问题
- **错误类型**：代码风格问题
- **具体描述**：命名不规范、代码冗余、缺乏文档
- **影响**：降低代码可读性、可维护性和可重用性

### 2. 主要问题分析

#### 2.1 命名问题
- **函数命名**：`calc` 不清晰，应该使用 `calculate_average`
- **变量命名**：`s`, `c`, `x`, `a` 含义不明确
- **不一致**：`FindPrimeNumbers`（驼峰式）与 `calc`（小写）不一致

#### 2.2 代码冗余
```python
s = s + x  # 可以简写为 s += x
c = c + 1  # 可以使用 len() 函数
2.3 缺乏文档和类型提示
没有函数文档字符串

没有参数和返回值的类型提示

没有说明函数的用途和边界条件

### 3. 修复建议
#### 3.1 改进命名
# 改进前
def calc(lst):
    s = 0
    c = 0

# 改进后
def calculate_average(numbers):
    total = 0
    count = 0
#### 3.2 简化代码
# 改进前
s = s + x
c = c + 1
# 改进后
total += number
# 或者直接使用内置函数
return sum(numbers) / len(numbers) if numbers else 0
#### 3.3 添加文档
def calculate_average(numbers: list[float]) -> float:
    '''计算数字列表的平均值
    
    Args:
        numbers: 包含数字的列表
        
    Returns:
        平均值，如果列表为空则返回0.0
        
    Raises:
        TypeError: 如果输入不是数字列表
    '''
### 4. 代码风格最佳实践
#### 4.1 命名约定
函数名：小写字母，下划线分隔（snake_case）

变量名：描述性的名词

常量名：全大写字母

类名：驼峰式（CamelCase）

#### 4.2 代码组织
一行不超过79字符

适当使用空行分隔逻辑块

避免过长的函数（一般不超过30行）

#### 4.3 注释和文档
为每个函数添加文档字符串

解释"为什么"而不是"是什么"

避免无意义的注释

### 5. 性能优化建议
质数查找优化：

# 原版：O(n²)时间复杂度
# 优化：只检查到平方根 O(n√n)
for divisor in range(2, int(num ** 0.5) + 1):
使用内置函数：

# 代替手动循环
total = sum(numbers)
count = len(numbers)
### 6. 教学提示
可读性重要性：代码被阅读的次数远多于被编写的次数

一致性：遵循团队或项目的代码风格指南

工具辅助：使用linter（如flake8、pylint）和formatter（如black）

### 7. 相关资源
PEP 8：Python代码风格指南

Google Python风格指南

项目特定的代码规范

### 8. 练习建议
重构一段风格不佳的代码

为现有代码添加类型提示和文档

使用代码检查工具分析自己的代码
"""
    expert_file = sample_dir / "expert_feedback.md"
    expert_file.write_text(expert_feedback, encoding='utf-8')
    print(f"创建专家反馈: {expert_file}")

    dataset_index = project_root / "dataset" / "dataset_index.json"
    new_sample = {
        "id": "sample_06",
        "category": "style_issue",
        "difficulty": "easy",
        "problem_description": "计算平均值和查找质数：实现两个函数：1）计算数字列表的平均值；2）查找小于等于给定限制的所有质数。注意代码的可读性和命名规范。",
        "student_code_path": "sample_06_style_issue/student_code.py",
        "reference_solution_path": "sample_06_style_issue/reference_solution.py",
        "test_cases_path": "sample_06_style_issue/test_cases.py",
        "expert_feedback_path": "sample_06_style_issue/expert_feedback.md",
        "tags": ["代码风格", "命名规范", "代码优化", "可读性"]
        }
    if dataset_index.exists():
        with open(dataset_index, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {"samples": []}
    existing_ids = [s["id"] for s in data["samples"]]
    if new_sample["id"] not in existing_ids:
        data["samples"].append(new_sample)
        print(f"添加新样本: {new_sample['id']}")
    else:
        print(f"样本 {new_sample['id']} 已存在，跳过添加")
    with open(dataset_index, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"更新数据集索引: {dataset_index}")
    print("\n" + "="*60)
    print("样本创建完成！")
    print(f"样本位置: {sample_dir}")
    print(f"样本ID: sample_06")
    print(f"错误类型: style_issue (代码风格)")
    print(f"难度: medium")
    print("="*60)
    print("\n验证创建的文件:")
    for file in sample_dir.iterdir():
        if file.is_file():
            size = file.stat().st_size
            print(f" {file.name}: {size} 字节")

    return sample_dir

if __name__ == "__main__":
    create_sample()
