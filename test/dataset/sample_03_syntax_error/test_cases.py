import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# 定义学生代码函数（修正语法错误后测试）
def student_find_maximum(numbers):
    if len(numbers) == 0:
        return None
    
    max_num = numbers[0]
    for num in numbers[1:]:
        if num > max_num:
            max_num = num
    
    return max_num

# 定义参考解决方案函数
def reference_find_maximum(numbers):
    if len(numbers) == 0:
        return None
    
    max_num = numbers[0]
    for num in numbers[1:]:
        if num > max_num:
            max_num = num
    
    return max_num

def test_empty_list():
    '''测试空列表'''
    # 学生代码（修正后）应该返回None
    result = student_find_maximum([])
    assert result is None, f"学生代码应返回None，实际返回{result}"
    
    result = reference_find_maximum([])
    assert result is None, f"参考代码应返回None，实际返回{result}"

def test_single_element():
    '''测试单个元素'''
    assert student_find_maximum([5]) == 5
    assert reference_find_maximum([5]) == 5

def test_positive_numbers():
    '''测试正数'''
    numbers = [1, 3, 2, 5, 4]
    assert student_find_maximum(numbers) == 5
    assert reference_find_maximum(numbers) == 5

def test_negative_numbers():
    '''测试负数'''
    numbers = [-1, -3, -2, -5, -4]
    assert student_find_maximum(numbers) == -1
    assert reference_find_maximum(numbers) == -1

def test_mixed_numbers():
    '''测试混合数'''
    numbers = [-5, 0, 5, -3, 3]
    assert student_find_maximum(numbers) == 5
    assert reference_find_maximum(numbers) == 5

def test_duplicate_max():
    '''测试重复最大值'''
    numbers = [1, 2, 3, 3, 2, 1]
    assert student_find_maximum(numbers) == 3
    assert reference_find_maximum(numbers) == 3

if __name__ == "__main__":
    test_empty_list()
    test_single_element()
    test_positive_numbers()
    test_negative_numbers()
    test_mixed_numbers()
    test_duplicate_max()
    print("所有测试通过！")
