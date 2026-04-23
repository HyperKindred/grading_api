import pytest
from student_code import reverse_two_digit

def test_middle_values():
    assert reverse_two_digit(45) == 54
    assert reverse_two_digit(37) == 73
    assert reverse_two_digit(11) == 11

def test_all_tens():
    for i in range(1, 10):
        n = i * 10
        assert reverse_two_digit(n) == i

def test_all_units():
    for i in range(1, 10):
        n = i
        # 注意：题目输入为两位数，故不应出现个位数，但若学生代码鲁棒，也可测试
        # 这里只测试两位数字，例如 12,23... 实际两位数字反转
        pass
    # 更系统的测试
    for tens in range(1, 10):
        for ones in range(0, 10):
            n = tens * 10 + ones
            expected = ones * 10 + tens
            assert reverse_two_digit(n) == expected