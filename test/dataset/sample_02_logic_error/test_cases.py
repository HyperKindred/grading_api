import pytest

# 直接在测试文件中定义两种解决方案
def student_calculate_average(numbers):
    total = sum(numbers)
    count = len(numbers)
    return total / count  # 如果numbers为空，这里会报错：ZeroDivisionError

def reference_calculate_average(numbers):
    if len(numbers) == 0:
        return 0
    total = sum(numbers)
    count = len(numbers)
    return total / count

def test_student_code():
    """测试学生代码"""
    # 测试空列表应该抛出异常
    with pytest.raises(ZeroDivisionError):
        student_calculate_average([])
    
    # 测试其他用例
    assert student_calculate_average([5]) == 5.0
    assert student_calculate_average([1, 2, 3, 4, 5]) == 3.0
    assert student_calculate_average([-1, -2, -3, -4, -5]) == -3.0
    assert student_calculate_average([-5, 0, 5]) == 0.0
    return True

def test_reference_code():
    """测试参考代码"""
    # 测试空列表应该返回0
    assert reference_calculate_average([]) == 0
    
    # 测试其他用例
    assert reference_calculate_average([5]) == 5.0
    assert reference_calculate_average([1, 2, 3, 4, 5]) == 3.0
    assert reference_calculate_average([-1, -2, -3, -4, -5]) == -3.0
    assert reference_calculate_average([-5, 0, 5]) == 0.0
    return True

if __name__ == "__main__":
    # 运行测试并输出结果
    results = []
    
    try:
        test_student_code()
        results.append("✓ 学生代码测试通过")
    except Exception as e:
        results.append(f"✗ 学生代码测试失败: {e}")
    
    try:
        test_reference_code()
        results.append("✓ 参考代码测试通过")
    except Exception as e:
        results.append(f"✗ 参考代码测试失败: {e}")
    
    for result in results:
        print(result)
    
    # 如果两个测试都通过，则返回0，否则返回1
    exit(0 if "失败" not in "".join(results) else 1)