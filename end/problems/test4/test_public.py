import pytest
import math
from student_code import triangle_area

def test_right_triangle():
    assert round(triangle_area(3, 4, 5), 2) == 6.00

def test_isosceles():
    assert round(triangle_area(5, 5, 6), 2) == 12.00

def test_equilateral():
    # 边长为2的等边三角形面积约为1.732
    assert round(triangle_area(2, 2, 2), 2) == 1.73

def test_small():
    assert round(triangle_area(1, 1, 1), 2) == 0.43