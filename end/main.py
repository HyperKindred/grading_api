from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from textwrap import dedent
from grader import CodeGrader
from fastapi.middleware.cors import CORSMiddleware
from llm_client import LLMClient
import asyncio
import json
from contextlib import asynccontextmanager
from pydantic import BaseModel
from db_config import get_db_connection
from db_utils import save_or_update_submission
app = FastAPI(title="编程作业智能评价系统")
from typing import Dict

grader = CodeGrader(problems_file='problems.json', use_docker=True)
llm_client = LLMClient()
MODELS = ["deepseek/deepseek-coder", "qwen/qwen-plus", "openai/gpt-4o"]
class CodeSubmission(BaseModel):
    problem_id: str
    code: str
    student_id: int
class LoginRequest(BaseModel):
    user_id: int
class UpdateSubmissionRequest(BaseModel):
    problem_id: str
    student_id: int
    scores: Dict[str, float]   # 例如 {"correctness": 45, "normativity": 18, ...}
    feedback: str
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 应用启动，资源初始化完成")
    yield
    print("🛑 应用关闭，清理资源...")
    await llm_client.close()
    print("✅ 资源清理完成")

app = FastAPI(title="编程作业智能评价系统", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite 默认端口
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/grade")
async def grade_code(submission: CodeSubmission):

    test_result = grader.run_tests_for_problem(submission.problem_id, submission.code)
    if "error" in test_result:
        raise HTTPException(status_code=400, detail=test_result["error"])
    
    # 正确性评分
    public = test_result['public']
    hidden = test_result['hidden']
    public_score = (public['passed'] / public['total']) * 10 if public['total'] > 0 else 0
    hidden_score = (hidden['passed'] / hidden['total']) * 10 if hidden['total'] > 0 else 0
    correctness_raw = public_score * 0.3 + hidden_score * 0.7  # 0-10
    correctness = correctness_raw * 5  # 转为50分制

    # 规范性评分
    pylint_issues = grader.get_pylint_issues(submission.code)
    pylint_issue_count = len(pylint_issues)
    normativity_raw = max(0, 10 - pylint_issue_count * 0.5)   # 手动计算得分
    normativity = normativity_raw * 2
    if pylint_issue_count > 0:
        pylint_details = "\n".join([f"  - 第{issue['line']}行: {issue['message']}" for issue in pylint_issues[:5]])
        if pylint_issue_count > 5:
            pylint_details += f"\n  ... 还有 {pylint_issue_count - 5} 个问题"
    else:
        pylint_details = "无"


    test_summary = f"公开测试: {public['passed']}/{public['total']} 通过; 隐藏测试: {hidden['passed']}/{hidden['total']} 通过"


    problem_meta = grader.problems.get(submission.problem_id)
    optimal_time = problem_meta.get("optimal_time_complexity", "O(n)") if problem_meta else "O(n)"
    optimal_space = problem_meta.get("optimal_space_complexity", "O(1)") if problem_meta else "O(1)"

    # 效率评分
    eff_task = llm_client.get_efficiency_score_async(
        submission.code, test_summary, MODELS,
        optimal_time=optimal_time,
        optimal_space=optimal_space
    )
    # 可读性评分
    read_task = llm_client.get_readability_score_async(submission.code, MODELS)
    eff_result, read_result = await asyncio.gather(eff_task, read_task)

    efficiency_raw = eff_result['score']   
    efficiency = efficiency_raw * 2        

    readability_raw = read_result['score']
    readability = readability_raw          

    total = correctness + normativity + efficiency + readability

    efficiency_analyses = eff_result['all_analyses']   
    readability_analyses = read_result['all_analyses']

    final_prompt = dedent(f"""
你是一位资深编程导师，请根据以下信息对学生代码进行综合评价，并给出3-5条具体改进建议。

**题目要求**：{problem_meta.get('description', '无')}

**学生代码**：
```python
{submission.code}
测试结果：
公开测试通过率：{public['passed']}/{public['total']}
隐藏测试通过率：{hidden['passed']}/{hidden['total']}
正确性得分（已加权）：{correctness_raw}/10 → 折合50分制为 {correctness}

规范性分析（Pylint）：
发现问题数量：{pylint_issue_count}
具体问题（部分展示）：
{pylint_details}
规范性得分：{normativity_raw}/10

效率维度评估（三个模型的独立分析）：

{MODELS[0]}: {efficiency_analyses[0] if len(efficiency_analyses)>0 else '无'}

{MODELS[1]}: {efficiency_analyses[1] if len(efficiency_analyses)>1 else '无'}

{MODELS[2]}: {efficiency_analyses[2] if len(efficiency_analyses)>2 else '无'}
综合效率得分：{efficiency_raw}/10

可读性维度评估（三个模型的独立分析）：

{MODELS[0]}: {readability_analyses[0] if len(readability_analyses)>0 else '无'}

{MODELS[1]}: {readability_analyses[1] if len(readability_analyses)>1 else '无'}

{MODELS[2]}: {readability_analyses[2] if len(readability_analyses)>2 else '无'}
综合可读性得分：{readability_raw}/10

请输出以下格式（纯文本，不需要JSON）：
【总体评价】
（一段话概括代码质量、优点和主要问题）

【具体改进建议】

...

...

...
""")
    final_feedback = await llm_client.get_combined_feedback(final_prompt, model="deepseek/deepseek-chat")
    scores_dict = {
        "correctness": round(correctness, 2),
        "normativity": round(normativity, 2),
        "efficiency": round(efficiency, 2),
        "readability": round(readability, 2),
        "total": round(total, 2)
    }
    save_or_update_submission(
        problem_id=submission.problem_id,
        student_id=submission.student_id,
        code=submission.code,
        scores_dict=scores_dict,
        feedback=final_feedback
    )
    return {
        "problem_id": submission.problem_id,
        "test_results": test_result,
        "scores": {
            "correctness": round(correctness, 2),
            "normativity": round(normativity, 2),
            "efficiency": round(efficiency, 2),
            "readability": round(readability, 2),
            "total": round(total, 2)
        },
        "feedback": final_feedback
    }

@app.get("/problems")
async def list_problems():
    """返回所有题目列表（id, title, difficulty）"""
    problems = []
    for pid, data in grader.problems.items():
        problems.append({
            "id": pid,
            "title": data.get("title", ""),
            "difficulty": data.get("difficulty", "unknown")
        })
    return problems

@app.get("/problems/{problem_id}")
async def get_problem(problem_id: str):
    """返回题目详情（不含测试用例）"""
    problem = grader.problems.get(problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="题目不存在")
    return {
        "id": problem_id,
        "title": problem.get("title", ""),
        "description": problem.get("description", ""),
        "difficulty": problem.get("difficulty", "unknown")
    }

@app.get("/")
async def root():
    return {"message": "智能代码批改系统 API 运行中"}

@app.post("/login")
async def login(req: LoginRequest):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, role, sid, name FROM users WHERE id = %s", (req.user_id,))
        user = cursor.fetchone()
        if not user:
            raise HTTPException(status_code=404, detail="用户不存在")
        if user['role'] == 'teacher':
            # 查询所有学生列表
            cursor.execute("SELECT id, sid, name FROM users WHERE role = 'student'")
            students = cursor.fetchall()
            return {"user": user, "students": students}
        else:
            return {"user": user}
        
@app.get("/api/users")
async def get_all_users():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, role, sid, name FROM users ORDER BY role, id")
        users = cursor.fetchall()
        return users
    
@app.get("/api/submission")
async def get_submission(problem_id: str, student_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT code, scores_json, feedback, tchange FROM submissions "
            "WHERE problem_id = %s AND student_id = %s",
            (problem_id, student_id)
        )
        row = cursor.fetchone()
        if row:
            return {
                "code": row["code"],
                "scores": json.loads(row["scores_json"]),
                "feedback": row["feedback"],
                "tchange": row["tchange"] == 1
            }
        return None
    
@app.post("/api/mark_read")
async def mark_tchange_read(problem_id: str, student_id: int):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE submissions SET tchange = 0 WHERE problem_id = %s AND student_id = %s",
            (problem_id, student_id)
        )
        conn.commit()
    return {"status": "ok"}

@app.get("/api/teacher/submissions")
async def get_teacher_submissions(problem_id: str):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT u.id as student_id, u.name, u.sid,
                   s.scores_json, s.feedback, s.schange, s.tchange, s.code
            FROM submissions s
            JOIN users u ON s.student_id = u.id
            WHERE s.problem_id = %s
            ORDER BY u.sid
        """, (problem_id,))
        rows = cursor.fetchall()
        result = []
        for row in rows:
            scores = json.loads(row["scores_json"])
            result.append({
                "student_id": row["student_id"],
                "name": row["name"],
                "sid": row["sid"],
                "scores": scores,
                "feedback": row["feedback"],
                "schange": row["schange"] == 1,
                "tchange": row["tchange"] == 1,
                "code": row["code"]
            })
        return result
@app.post("/api/teacher/update_submission")
async def update_submission(req: UpdateSubmissionRequest):
    scores_json = json.dumps(req.scores)
    with get_db_connection() as conn:
        cursor = conn.cursor()
        # 更新 submissions 表，设置 tchange=1, schange=0（教师已读）
        cursor.execute("""
            UPDATE submissions
            SET scores_json = %s, feedback = %s, tchange = 1, schange = 0
            WHERE problem_id = %s AND student_id = %s
        """, (scores_json, req.feedback, req.problem_id, req.student_id))
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="提交记录不存在")
        conn.commit()
    return {"status": "ok"}
