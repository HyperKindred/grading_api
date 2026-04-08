## 诊断报告 (样本ID: sample_04_runtime_error)

### 1. 核心问题
- **错误类型**：运行时错误（KeyError）
- **具体描述**：直接访问字典中可能不存在的键
- **错误行**：`return users[username]`

### 2. 错误分析
当尝试访问字典中不存在的键时，Python会抛出KeyError。这是常见的运行时错误之一。

### 3. 解决方案
有三种方式可以安全地访问字典：

**方案1：使用get方法（推荐）**
```python
def get_user_email(users, username):
    return users.get(username)  # 键不存在时返回None
**方案2：使用in检查**
def get_user_email(users, username):
    if username in users:
        return users[username]
    return None  # 或者抛出异常，根据需求决定
**方案3：使用try-except处理**
def get_user_email(users, username):
    try:
        return users[username]
    except KeyError:
        return None  # 或者抛出自定义异常
## 4. 教学提示与延伸思考
防御性编程：总是假设输入可能不符合预期

错误处理策略：根据上下文决定返回默认值还是抛出异常

字典方法：介绍get()、setdefault()、in操作符等字典方法
## 5. 代码优化建议
1. 添加默认值：
return users.get(username, "unknown@example.com")
2. 使用类型提示：
def get_user_email(users: dict[str, str], username: str) -> str | None:
3. 考虑性能：in检查和get()方法的时间复杂度都是O(1)

## 6. 相关练习
实现一个安全的列表访问函数

编写一个处理多种异常类型的函数

练习使用defaultdict简化代码
## 7. 扩展知识
collections.defaultdict 的使用

字典视图对象（keys(), values(), items()）

字典推导式
