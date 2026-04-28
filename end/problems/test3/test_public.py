import pytest
from student_code import reverse_two_digit

def test_normal():
    assert reverse_two_digit(98) == 89

def test_ending_with_zero():
    assert reverse_two_digit(20) == 2

def test_smallest():
    assert reverse_two_digit(10) == 1

def test_largest():
    assert reverse_two_digit(99) == 99