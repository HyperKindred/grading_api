import pytest
from student_code import circle_area

def test_negative_radius():
    # 负数半径按数学定义面积应为正（平方后为正），但一般约定半径非负。
    # 这里测试学生是否处理了负数（直接平方得到正数，或抛出异常均可）。
    # 我们要求直接平方计算，因为面积总是非负。
    assert circle_area(-3) == 3.14159 * 9

def test_very_small_float():
    r = 0.0001
    expected = 3.14159 * 1e-8
    assert abs(circle_area(r) - expected) < 1e-12

def test_irrational_radius():
    r = 2.0 ** 0.5  # sqrt(2)
    expected = 3.14159 * 2
    assert abs(circle_area(r) - expected) < 1e-6

def test_rounding_edge():
    # 面积恰好为整数边界时，保留两位小数
    r = (10 / 3.14159) ** 0.5  # 使面积接近10
    area = circle_area(r)
    # 只检查不报错即可
    assert isinstance(area, float)