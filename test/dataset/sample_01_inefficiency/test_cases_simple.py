from student_code import Solution as StudentSolution
from reference_solution import Solution as ReferenceSolution
import pytest
import time

TEST_CASES = [
    ([2, 7, 11, 15], 9, [0, 1]),
    ([3, 2, 4], 6, [1, 2]),
    ([3, 3], 6, [0, 1]),
    ([0, 4, 3, 0], 0, [0, 3]),
    ([-1, -2, -3, -4, -5], -8, [2, 4]),
]

def test_student_solution():
    """测试学生代码的功能正确性"""
    solution = StudentSolution()
    
    for nums, target, expected in TEST_CASES:
        result = solution.twoSum(nums, target)
        assert result == expected, f"输入{nums}, 目标{target}: 期望{expected}, 得到{result}"
    
    # 空数组测试
    assert solution.twoSum([], 5) == []
    
    print("学生代码功能测试: 5/5 通过")

def test_reference_solution():
    """测试参考代码的功能正确性"""
    solution = ReferenceSolution()
    
    for nums, target, expected in TEST_CASES:
        result = solution.twoSum(nums, target)
        assert result == expected, f"输入{nums}, 目标{target}: 期望{expected}, 得到{result}"
    
    print("参考代码功能测试: 5/5 通过")

def test_performance_comparison():
    """性能对比测试（小规模）"""
    student = StudentSolution()
    reference = ReferenceSolution()
    
    # 小规模测试
    nums = list(range(100))
    target = 197
    
    start = time.time()
    student_result = student.twoSum(nums, target)
    student_time = time.time() - start
    
    start = time.time()
    reference_result = reference.twoSum(nums, target)
    reference_time = time.time() - start
    
    assert student_result == [98, 99]
    assert reference_result == [98, 99]
    
    print(f"性能对比 (100元素):")
    print(f"  学生代码: {student_time:.4f}秒")
    print(f"  参考代码: {reference_time:.4f}秒")
    print(f"  效率提升: {student_time/reference_time:.1f}倍")

if __name__ == "__main__":
    test_student_solution()
    test_reference_solution()
    test_performance_comparison()
    print("\n所有测试通过！")