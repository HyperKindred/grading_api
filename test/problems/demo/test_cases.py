try:
    from student_code import add
except ImportError:
    print("错误：找不到 student_code.py 或 add 函数")
    exit(1)

def test_add_basic():
    assert add(2, 3) == 5, "2 + 3 应该等于 5"
    assert add(-1, 1) == 0, "-1 + 1 应该等于 0"

def test_add_edge_cases():
    assert add(0, 0) == 0, "0 + 0 应该等于 0"
    assert add(100, -100) == 0, "100 + (-100) 应该等于 0"