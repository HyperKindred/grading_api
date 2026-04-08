import pytest
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
