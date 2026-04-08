from student_code import concat_strings

def test_long_strings():
    a = "x" * 100
    b = "y" * 100
    c = "z" * 100
    expected = a + " " + b + " " + c
    assert concat_strings(a, b, c) == expected

def test_numbers():
    assert concat_strings("123", "456", "789") == "123 456 789"

def test_mixed():
    assert concat_strings("@#$", " ", "end") == "@#$   end"  # 中间是两个空格