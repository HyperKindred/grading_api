import pytest
from student_code import circle_area

def test_positive_integer():
    assert round(circle_area(2), 2) == 12.57   # 3.14159 * 4 = 12.56636 -> 12.57

def test_positive_float():
    assert round(circle_area(1.5), 2) == 7.07  # 3.14159 * 2.25 = 7.0685775 -> 7.07

def test_zero():
    assert circle_area(0) == 0.0

def test_large_number():
    assert round(circle_area(100), 2) == 31415.9  # 3.14159 * 10000 = 31415.9