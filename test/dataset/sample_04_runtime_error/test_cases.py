import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

# 定义学生代码函数
def student_get_user_email(users, username):
    return users[username]  # 可能抛出KeyError

# 定义参考解决方案函数
def reference_get_user_email(users, username):
    return users.get(username)

def test_existing_user():
    '''测试存在的用户'''
    users = {"alice": "alice@example.com", "bob": "bob@example.com"}
    
    # 学生代码
    result = student_get_user_email(users, "alice")
    assert result == "alice@example.com"
    
    # 参考代码
    result = reference_get_user_email(users, "alice")
    assert result == "alice@example.com"

def test_non_existing_user_student():
    '''测试学生代码处理不存在的用户（应该抛出KeyError）'''
    users = {"alice": "alice@example.com"}
    
    with pytest.raises(KeyError):
        student_get_user_email(users, "bob")

def test_non_existing_user_reference():
    '''测试参考代码处理不存在的用户（应该返回None）'''
    users = {"alice": "alice@example.com"}
    
    result = reference_get_user_email(users, "bob")
    assert result is None

def test_empty_dict_student():
    '''测试学生代码处理空字典'''
    with pytest.raises(KeyError):
        student_get_user_email({}, "alice")

def test_empty_dict_reference():
    '''测试参考代码处理空字典'''
    result = reference_get_user_email({}, "alice")
    assert result is None

def test_none_value():
    '''测试值为None的情况'''
    users = {"alice": None, "bob": "bob@example.com"}
    
    # 学生代码
    result = student_get_user_email(users, "alice")
    assert result is None
    
    # 参考代码
    result = reference_get_user_email(users, "alice")
    assert result is None

def test_case_sensitive():
    '''测试大小写敏感性'''
    users = {"Alice": "alice@example.com"}
    
    with pytest.raises(KeyError):
        student_get_user_email(users, "alice")  # 小写
    
    result = reference_get_user_email(users, "alice")
    assert result is None

if __name__ == "__main__":
    test_existing_user()
    test_non_existing_user_reference()
    test_empty_dict_reference()
    test_none_value()
    test_case_sensitive()
    print("参考代码测试通过！")
    print("注意：学生代码测试会抛出KeyError，这是预期行为")
