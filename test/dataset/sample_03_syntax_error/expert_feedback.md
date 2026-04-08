## 诊断报告 (样本ID: sample_03_syntax_error)

### 1. 核心问题
- **错误类型**：语法错误
- **具体描述**：if语句缺少冒号（:）
- **错误行**：第3行

### 2. 错误分析
```python
if len(numbers) == 0  # ❌ 缺少冒号
    return None
在Python中，所有控制流语句（if、for、while、def、class等）都需要以冒号结尾。
###3. 修复步骤
在第3行的if语句末尾添加冒号

修改后的代码：
if len(numbers) == 0:  # ✅ 正确的语法
    return None
###4. 教学提示与延伸思考
- **语法规则**：强调Python的缩进和冒号语法

- **常见错误**：列举其他常见的语法错误（缩进、括号不匹配、引号不闭合等）

- **调试技巧**：使用IDE的语法高亮和检查功能

###5. 代码优化建议
添加类型提示：
def find_maximum(numbers: list) -> int:
使用内置函数：
return max(numbers) if numbers else None
添加文档字符串说明函数功能
###6. 预防措施
使用代码编辑器或IDE的语法检查

在提交代码前运行语法检查：python -m py_compile student_code.py

遵循PEP 8代码风格指南

###7. 相关练习
修复其他常见的语法错误

编写一个检查列表最小值的函数

练习使用try-except处理可能的错误
