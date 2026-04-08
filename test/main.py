from fastapi import FastAPI
from pydantic import BaseModel
import os
import grader
from llm_client import LLMClient  # 导入 LLMClient 类

app = FastAPI()

class CodeSubmission(BaseModel):
    problem_id: str
    code: str

@app.post("/grade")
async def grade_code(submission: CodeSubmission):
    # 1. 为每个题目创建目录并保存代码
    problem_dir = os.path.join("problems", submission.problem_id)
    os.makedirs(problem_dir, exist_ok=True)
    
    student_code_file = os.path.join(problem_dir, "student_code.py")
    with open(student_code_file, "w", encoding="utf-8") as f:
        f.write(submission.code)
    
    # 2. 运行测试
    test_output = grader.run_tests(submission.problem_id)
    
    # 3. 调用 LLM 生成反馈（使用 LLMClient）
    llm = LLMClient()  # 创建客户端实例
    model_name = "deepseek/deepseek-chat"  # 你可以换成你选定的模型，如 "openai/gpt-4o" 或 "qwen/qwen-plus"
    result = llm.get_feedback(submission.code, test_output, model_name)
    
    if result.status == "success":
        ai_feedback = result.feedback
    else:
        ai_feedback = f"LLM 调用失败: {result.error_message}"
    
    # 4. 返回结果
    return {
        "problem_id": submission.problem_id,
        "test_output": test_output,
        "ai_feedback": ai_feedback,
        "status": "success"
    }

@app.get("/")
def read_root():
    return {"message": "智能代码批改系统 API 正在运行 (简化版)"}