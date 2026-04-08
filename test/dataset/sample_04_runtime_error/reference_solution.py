def get_user_email(users, username):
    # 安全地访问字典：使用get方法
    return users.get(username)  # 如果键不存在，返回None

# 或者使用in检查
def get_user_email_safe(users, username):
    if username in users:
        return users[username]
    return None

# 示例使用
users = {"alice": "alice@example.com", "bob": "bob@example.com"}
print(get_user_email(users, "alice"))  # "alice@example.com"
print(get_user_email(users, "charlie"))  # None
