import os
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
from dotenv import load_dotenv
import asyncio
import aiohttp
load_dotenv()  # 加载 .env 文件

# 模型配置类
@dataclass
class ModelConfig:
    """模型配置信息"""
    name: str
    display_name: str
    category: str  # 如: openai, open_source, code_specialized
    max_tokens: int = 1024
    temperature: float = 0.7

# 模型反馈结果类
@dataclass
class ModelFeedbackResult:
    """模型反馈结果"""
    model_name: str
    feedback: str
    status: str  # success, error, timeout
    response_time: float
    token_count: Optional[int] = None
    error_message: Optional[str] = None

# 常用模型配置
# 常用模型配置
MODEL_CONFIGS = {
    "openai/gpt-4o": ModelConfig(
        name="openai/gpt-4o",
        display_name="GPT-4o",
        category="openai"
    ),
    "deepseek/deepseek-coder": ModelConfig(
        name="deepseek/deepseek-coder",
        display_name="DeepSeek Coder",
        category="code_specialized"
    ),
    "qwen/qwen-plus": ModelConfig(
        name="qwen/qwen-plus",
        display_name="Qwen Plus",
        category="open_source"
    ),
}

# 默认的代码分析模型列表
DEFAULT_CODE_MODELS = [
    "openai/gpt-4o",
    "deepseek/deepseek-coder",
    "qwen/qwen-plus",
]

class LLMClient:
    """LLM客户端类，封装OpenRouter API调用"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://openrouter.ai/api/v1"):
        """
        初始化LLM客户端
        
        Args:
            api_key: OpenRouter API密钥，如果为None则从环境变量读取
            base_url: API基础URL
        """
        self.api_key = api_key or os.getenv("OPENROUTER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenRouter API密钥未设置。请设置OPENROUTER_API_KEY环境变量或传入api_key参数")
        
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self._session: Optional[aiohttp.ClientSession] = None
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建共享的 aiohttp session"""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(headers=self.headers)
        return self._session

    async def _async_post(self, model: str, prompt: str, timeout: int = 30) -> dict:
        """异步发送请求到 OpenRouter，返回解析后的 JSON（包含 score, confidence 等）"""
        session = await self._get_session()
        url = f"{self.base_url}/chat/completions"
        
        # 针对效率评分使用低 temperature 保证稳定性
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
            "max_tokens": 300,
        }
        try:
            async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    return {"score": 5.0, "confidence": 0.0, "analysis": f"HTTP {resp.status}: {text}"}
                result = await resp.json()
                content = result["choices"][0]["message"]["content"]
                # 尝试解析 JSON
                try:
                    # 提取 JSON 部分（防止模型输出额外文字）
                    import re
                    json_match = re.search(r'\{.*\}', content, re.DOTALL)
                    if json_match:
                        parsed = json.loads(json_match.group())
                        score = int(parsed.get("score", 5))
                        confidence = float(parsed.get("confidence", 0.5))
                        analysis = parsed.get("analysis", "")
                        return {"score": score, "confidence": confidence, "analysis": analysis}
                    else:
                        return {"score": 5, "confidence": 0.3, "analysis": "模型未返回有效JSON"}
                except Exception:
                    return {"score": 5, "confidence": 0.3, "analysis": "JSON解析失败"}
        except asyncio.TimeoutError:
            return {"score": 5, "confidence": 0.2, "analysis": "请求超时"}
        except Exception as e:
            return {"score": 5, "confidence": 0.2, "analysis": f"请求异常: {str(e)}"}
    
    def _build_code_analysis_prompt(self, code: str, test_results: str) -> str:
        """构建代码分析提示词（简化版）"""
        return f"""你是一位经验丰富的编程导师，请严格按以下格式提供代码反馈：

代码：
```python
{code}
```
测试结果：
{test_results}

请从4个维度评分（1-5分）并详细分析：

【综合评分】

正确性：[分数]/5（是否实现题目要求？测试失败原因？）

效率：[分数]/5（时间复杂度/空间复杂度优化空间？）

可读性：[分数]/5（代码格式、命名、注释是否清晰？）

规范性：[分数]/5（是否符合Python PEP 8规范？）

【详细分析】
[请详细分析代码优缺点...]

【具体修改建议】
[至少提供3条具体改进建议...]

注意：请确保评分是整数（如3/5），不要使用"分"字。"""
    def get_feedback(
        self, 
        code: str, 
        test_results: str, 
        model_name: str, 
        timeout: int = 30,
        **kwargs
    ) -> ModelFeedbackResult:
        """
        获取单个模型的反馈
        """
        start_time = time.time()
        
        # 获取模型配置
        model_config = MODEL_CONFIGS.get(model_name)
        if model_config:
            temperature = kwargs.get('temperature', model_config.temperature)
            max_tokens = kwargs.get('max_tokens', model_config.max_tokens)
        else:
            temperature = kwargs.get('temperature', 0.7)
            max_tokens = kwargs.get('max_tokens', 1024)
        
        # 特别处理某些模型
        if model_name in ["z-ai/glm-4.7", "minimax/minimax-m2.1", "google/gemini-2.5-pro"]:
            # 这些模型可能需要更大的max_tokens
            max_tokens = max(max_tokens, 2048)
        try:
            url = f"{self.base_url}/chat/completions"
            prompt = self._build_code_analysis_prompt(code, test_results)
            
            # 针对某些模型使用简化的消息结构
            if model_name in ["z-ai/glm-4.7", "minimax/minimax-m2.1", "google/gemini-2.5-pro"]:
                # 简化版：只使用用户消息
                messages = [
                    {"role": "user", "content": prompt}
                ]
            else:
                # 标准版：包含系统消息
                messages = [
                    {"role": "system", "content": "你是一位严谨的编程导师，擅长分析代码质量和提供改进建议。"},
                    {"role": "user", "content": prompt}
                ]
            
            data = {
                "model": model_name,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **{k: v for k, v in kwargs.items() if k not in ['temperature', 'max_tokens']}
            }
            
            # 关键修复：使用 json.dumps 确保正确编码
            json_data = json.dumps(data, ensure_ascii=False)
            
            # 修改请求头，添加编码信息
            headers = self.headers.copy()
            headers["Content-Type"] = "application/json; charset=utf-8"
            
            # 发送请求 - 只使用 data 参数
            response = requests.post(
                url, 
                headers=headers, 
                data=json_data.encode('utf-8'),
                timeout=timeout
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})
            
            response_time = time.time() - start_time
            
            return ModelFeedbackResult(
                model_name=model_name,
                feedback=content,
                status="success",
                response_time=response_time,
                token_count=usage.get("total_tokens")
            )
            
        except requests.exceptions.Timeout:
            response_time = time.time() - start_time
            return ModelFeedbackResult(
                model_name=model_name,
                feedback="",
                status="timeout",
                response_time=response_time,
                error_message="请求超时"
            )
        except Exception as e:
            response_time = time.time() - start_time
            return ModelFeedbackResult(
                model_name=model_name,
                feedback="",
                status="error",
                response_time=response_time,
                error_message=str(e)
            )


    def get_available_models(self, category: Optional[str] = None) -> List[ModelConfig]:
        """
        获取可用模型列表
        
        Args:
            category: 按类别过滤（如: openai, open_source, code_specialized）
            
        Returns:
            模型配置列表
        """
        if category:
            return [config for config in MODEL_CONFIGS.values() if config.category == category]
        return list(MODEL_CONFIGS.values())

    async def get_efficiency_score_async(self, code: str, test_output: str, 
                                        models: list, 
                                        optimal_time: str = "O(n)", 
                                        optimal_space: str = "O(1)") -> dict:
        prompt = f"""你是一个算法效率评估专家。请根据以下规则，为学生代码的效率评分（0-10分）。

**题目要求的最优时间复杂度**：{optimal_time}
**题目要求的最优空间复杂度**：{optimal_space}

评分原则：
- 如果学生代码的时间复杂度等于或优于最优时间复杂度，且空间复杂度满足要求 → 10分
- 如果时间复杂度比最优复杂度差一个等级（例如最优 O(n)，学生 O(n²)） → 5-7分
- 如果差两个等级或更多（例如最优 O(n)，学生 O(2ⁿ)） → 0-4分
- 如果代码中有严重的效率问题（如重复计算、死循环） → 酌情扣分

代码：
{code}

测试输出（可能包含超时信息）：
{test_output}

你必须返回 JSON 格式：{{"score": 整数(0-10), "confidence": 浮点数(0-1), "analysis": "简短中文分析"}}
"""
        tasks = [self._async_post(model, prompt) for model in models]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        scores = []
        confidences = []
        all_analyses = []
        model_names = []
        for i, res in enumerate(results):
            if isinstance(res, dict) and 'score' in res:
                score = max(0, min(10, res['score']))
                scores.append(score)
                confidences.append(res.get('confidence', 0.5))
                all_analyses.append(res.get('analysis', '无分析'))
                model_names.append(models[i])
            else:
                scores.append(5.0)
                confidences.append(0.3)
                all_analyses.append("模型调用失败")
                model_names.append(models[i])

        if not scores:
            return {'score': 5.0, 'analysis': '无法获取模型评分'}

        total_weight = sum(confidences)
        weighted_score = sum(s * c for s, c in zip(scores, confidences)) / total_weight
        return {
            'score': round(weighted_score, 2),
            'all_analyses': all_analyses,
            'model_names': model_names
        }
    async def get_readability_score_async(self, code: str, models: list) -> dict:
        prompt = f"""你是一个代码质量评估专家。请评估以下代码的可读性，考虑命名清晰度、代码结构、注释质量、整体可理解性，给出0-10的评分（10分最优）。同时给出你对评分的置信度（0-1）。

    评分参考：
    - 10分：命名清晰，结构优雅，注释充分
    - 8-9分：命名良好，结构清晰，缺少少量注释
    - 6-7分：命名基本可读，结构一般，缺少注释
    - 4-5分：命名模糊，结构混乱，无注释
    - 1-3分：代码难以理解，逻辑混乱
    - 0分：完全无法阅读

    代码：
    {code}
    输出 JSON 格式：{{"score": 整数, "confidence": 浮点数, "analysis": "简短分析"}}"""
               # 并发调用所有模型
        tasks = [self._async_post(model, prompt) for model in models]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # 解析并融合结果
        scores = []
        confidences = []
        all_analyses = []
        model_names = []
        for i, res in enumerate(results):
            if isinstance(res, dict) and 'score' in res:
                # 确保分数在 0-10 范围内
                score = max(0, min(10, res['score']))
                scores.append(score)
                confidences.append(res.get('confidence', 0.5))
                all_analyses.append(res.get('analysis', '无分析'))
                model_names.append(models[i])
            else:
                # 模型调用失败，用默认值填充（置信度低）
                scores.append(5.0)
                confidences.append(0.3)
                all_analyses.append("模型调用失败")
                model_names.append(models[i])

        if not scores:
            return {'score': 5.0, 'analysis': '无法获取模型评分'}

        # 加权平均（置信度作为权重）
        total_weight = sum(confidences)
        weighted_score = sum(s * c for s, c in zip(scores, confidences)) / total_weight
        # 取第一条分析作为简要反馈（可优化为融合）
        return {
            'score': round(weighted_score, 2),   # 0-10 分
            'all_analyses': all_analyses, 
            'model_names': model_names
    }

    async def get_combined_feedback(self, prompt: str, model: str = "deepseek/deepseek-chat") -> str:
        """生成综合反馈（纯文本）"""
        session = await self._get_session()
        url = f"{self.base_url}/chat/completions"
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1500,
        }
        try:
            async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=60)) as resp:
                # 先检查 HTTP 状态码
                if resp.status != 200:
                    error_text = await resp.text()
                    print(f"OpenRouter 返回错误 {resp.status}: {error_text}")
                    return f"综合反馈生成失败：HTTP {resp.status} - {error_text[:200]}"
                
                result = await resp.json()
                # 检查是否有错误字段
                if "error" in result:
                    error_msg = result["error"].get("message", str(result["error"]))
                    print(f"OpenRouter API 错误: {error_msg}")
                    return f"综合反馈生成失败：{error_msg}"
                
                # 检查 choices 字段
                if "choices" not in result or len(result["choices"]) == 0:
                    print(f"响应中没有 choices: {result}")
                    return "综合反馈生成失败：API 响应格式异常"
                
                return result["choices"][0]["message"]["content"]
        except asyncio.TimeoutError:
            return "综合反馈生成失败：请求超时"
        except Exception as e:
            print(f"综合反馈异常: {e}")
            return f"综合反馈生成失败：{str(e)}"

    async def close(self):
        if self._session:
            await self._session.close()