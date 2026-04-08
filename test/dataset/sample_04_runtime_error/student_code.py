def get_user_email(users, username):
    # 运行时错误：直接访问可能不存在的键
    return users[username]  # 如果username不在users中，会抛出KeyError

# 示例使用
users = {"alice": "alice@example.com", "bob": "bob@example.com"}
print(get_user_email(users, "alice"))  # 正常
print(get_user_email(users, "charlie"))  # KeyError
