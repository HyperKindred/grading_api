# 从学生代码中导入函数
from student_code import concat_strings

def test_basic():
    assert concat_strings("123", "456", "hello") == "123 456 hello"

def test_empty():
    assert concat_strings("", "", "") == "  "  # 三个空字符串，中间有空格

def test_with_spaces():
    assert concat_strings("a b", "c", "d") == "a b c d"

def test_unicode():
    assert concat_strings("你好", "世界", "！") == "你好 世界 ！"