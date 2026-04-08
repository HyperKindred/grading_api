import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# 定义学生代码函数
def student_get_middle_element(lst):
    middle_index = len(lst) // 2
    return lst[middle_index]

# 定义参考解决方案函数
def reference_get_middle_element(lst):
    if not lst:
        return None
    middle_index = len(lst) // 2
    return lst[middle_index]

def test_empty_list_student():
    '''测试学生代码处理空列表（应该抛出IndexError）'''
    with pytest.raises(IndexError):
        student_get_middle_element([])

def test_empty_list_reference():
    '''测试参考代码处理空列表（应该返回None）'''
    result = reference_get_middle_element([])
    assert result is None

def test_single_element():
    '''测试单个元素'''
    assert student_get_middle_element([5]) == 5
    assert reference_get_middle_element([5]) == 5

def test_odd_length():
    '''测试奇数长度列表'''
    lst = [1, 2, 3, 4, 5]
    assert student_get_middle_element(lst) == 3
    assert reference_get_middle_element(lst) == 3

def test_even_length():
    '''测试偶数长度列表'''
    lst = [1, 2, 3, 4]
    # 对于偶数长度，Python的整数除法会向下取整
    assert student_get_middle_element(lst) == 3  # len=4, 4//2=2, lst[2]=3
    assert reference_get_middle_element(lst) == 3

def test_negative_numbers():
    '''测试负数'''
    lst = [-5, -3, 0, 3, 5]
    assert student_get_middle_element(lst) == 0
    assert reference_get_middle_element(lst) == 0

def test_string_list():
    '''测试字符串列表'''
    lst = ["a", "b", "c", "d", "e"]
    assert student_get_middle_element(lst) == "c"
    assert reference_get_middle_element(lst) == "c"

def test_mixed_types():
    '''测试混合类型（应该正常处理）'''
    lst = [1, "two", 3.0, [4, 5]]
    assert student_get_middle_element(lst) == 3.0
    assert reference_get_middle_element(lst) == 3.0

if __name__ == "__main__":
    test_single_element()
    test_odd_length()
    test_even_length()
    test_negative_numbers()
    test_string_list()
    test_mixed_types()
    test_empty_list_reference()
    print("参考代码测试通过！")
    print("注意：学生代码的空列表测试会抛出IndexError，这是预期行为")
