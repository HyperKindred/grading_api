import os
import json
import requests
from typing import Dict

def evaluate_with_llm_judge(
    model_feedbacks: Dict[str, str], 
    context: str,
    judge_model: str = "openai/gpt-4o"
) -> Dict:
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("未设置 OPENROUTER_API_KEY")
    
    feedbacks_formatted = "\n\n".join(
        [f"【模型 {model_name} 的反馈】\n{feedback}" 
         for model_name, feedback in model_feedbacks.items()]
    )
    
    evaluation_prompt = f"""
任务背景
你是一位编程教育评估专家，需要公正地评估不同AI模型对同一份学生代码的反馈质量。

评估上下文
{context}

待评估的模型反馈
{feedbacks_formatted}

评估维度与标准（每项1-5分）
1. 诊断准确性：指出的问题是否与代码真实缺陷完全一致？
2. 建议实用性：修改建议是否具体、安全、可立即执行？
3. 解释教学性：解释是否清晰易懂，能帮助学生理解概念？
4. 格式规范性：是否遵循了要求的格式和结构？
5. 综合教育价值：整体反馈是否对初学者有显著帮助？

评估要求
1. 为每个模型在每个维度上打分（1-5分整数）
2. 提供简短的定性评语（每个模型1-2句话）
3. 最后给出整体排名和推荐理由
4. 保持绝对中立，不考虑模型名称或品牌

请以严格的JSON格式回复，结构如下：
{{
  "evaluations": {{
    "模型A名称": {{
      "scores": {{"诊断准确性": 5, "建议实用性": 4, "解释教学性": 5, "格式规范性": 4, "综合教育价值": 5}},
      "comments": "定性评语..."
    }}
  }},
  "ranking": ["最佳模型名称", "次佳模型名称"],
  "summary": "整体分析与推荐理由"
}}
"""
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": judge_model,
        "messages": [
            {"role": "system", "content": "你是一位公正、严谨的教育评估专家，必须严格遵循指令要求。"},
            {"role": "user", "content": evaluation_prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 2000,
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=45
        )
        response.raise_for_status()
        result = response.json()
        return json.loads(result["choices"][0]["message"]["content"])
    except Exception as e:
        return {"error": f"LLM裁判评估失败: {str(e)}"}