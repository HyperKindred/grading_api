import pytest
import math
from student_code import triangle_area

def test_typical():
    assert round(triangle_area(6, 8, 10), 2) == 24.00
    assert round(triangle_area(5, 12, 13), 2) == 30.00

def test_very_flat():
    # 接近退化的三角形，面积很小
    a, b, c = 2, 3, 4
    s = (a+b+c)/2
    expected = math.sqrt(s*(s-a)*(s-b)*(s-c))
    assert abs(triangle_area(a, b, c) - expected) < 1e-6

def test_large_values():
    a, b, c = 100, 150, 200
    s = (a+b+c)/2
    expected = math.sqrt(s*(s-a)*(s-b)*(s-c))
    assert abs(triangle_area(a, b, c) - expected) < 1e-6

def test_float_precision():
    a, b, c = 3.5, 4.2, 5.1
    s = (a+b+c)/2
    expected = math.sqrt(s*(s-a)*(s-b)*(s-c))
    assert abs(triangle_area(a, b, c) - expected) < 1e-6