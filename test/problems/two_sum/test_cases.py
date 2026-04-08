from student_code import two_sum  # 导入学生写的函数

def test_basic():
    assert two_sum([2,7,11,15], 9) == [0,1]

def test_no_solution():
    assert two_sum([1,2,3], 7) == []

def test_duplicate():
    assert two_sum([3,3], 6) == [0,1]