from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from textwrap import dedent
from grader import CodeGrader
from fastapi.middleware.cors import CORSMiddleware
from llm_client import LLMClient
import asyncio
from contextlib import asynccontextmanager
app = FastAPI(title="编程作业智能评价系统")

# 初始化代码执行器
grader = CodeGrader(problems_file='problems.json')
llm_client = LLMClient()
MODELS = ["deepseek/deepseek-coder", "qwen/qwen-plus", "openai/gpt-4o"]
class CodeSubmission(BaseModel):
    problem_id: str
    code: str

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动时执行（可在此处初始化资源）
    print("🚀 应用启动，资源初始化完成")
    yield
    # 关闭时执行
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
    # 1. 运行测试
    test_result = grader.run_tests_for_problem(submission.problem_id, submission.code)
    if "error" in test_result:
        raise HTTPException(status_code=400, detail=test_result["error"])
    
    # 2. 正确性评分（公开测试占30%，隐藏占70%）
    public = test_result['public']
    hidden = test_result['hidden']
    public_score = (public['passed'] / public['total']) * 10 if public['total'] > 0 else 0
    hidden_score = (hidden['passed'] / hidden['total']) * 10 if hidden['total'] > 0 else 0
    correctness_raw = public_score * 0.3 + hidden_score * 0.7  # 0-10
    correctness = correctness_raw * 5  # 转为50分制

    # 3. 规范性评分（Pylint）
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

     # 准备测试摘要（用于效率评分的参考）
    test_summary = f"公开测试: {public['passed']}/{public['total']} 通过; 隐藏测试: {hidden['passed']}/{hidden['total']} 通过"

    # 获取题目元数据（必须在调用效率评分之前）
    problem_meta = grader.problems.get(submission.problem_id)
    optimal_time = problem_meta.get("optimal_time_complexity", "O(n)") if problem_meta else "O(n)"
    optimal_space = problem_meta.get("optimal_space_complexity", "O(1)") if problem_meta else "O(1)"

    # 并发获取效率评分
    eff_task = llm_client.get_efficiency_score_async(
        submission.code, test_summary, MODELS,
        optimal_time=optimal_time,
        optimal_space=optimal_space
    )
    read_task = llm_client.get_readability_score_async(submission.code, MODELS)
    eff_result, read_result = await asyncio.gather(eff_task, read_task)

    efficiency_raw = eff_result['score']   # 0-10
    efficiency = efficiency_raw * 2        # 转为20分制

    # 可读性暂时保留默认值，后续再实现
    readability_raw = read_result['score']
    readability = readability_raw          # 0-10

    # 计算总分
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
    # 只返回元数据，不返回测试用例路径
    return {
        "id": problem_id,
        "title": problem.get("title", ""),
        "description": problem.get("description", ""),
        "difficulty": problem.get("difficulty", "unknown")
    }

@app.get("/")
async def root():
    return {"message": "智能代码批改系统 API 运行中"}

