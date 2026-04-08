import os
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import requests
from dotenv import load_dotenv

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
    "openai/gpt-4-turbo": ModelConfig(
        name="openai/gpt-4-turbo",
        display_name="GPT-4 Turbo",
        category="openai"
    ),
    "anthropic/claude-3-5-sonnet": ModelConfig(
        name="anthropic/claude-3-5-sonnet",
        display_name="Claude 3.5 Sonnet",
        category="anthropic",
        max_tokens=2048,
        temperature=0.4,  # 适中的随机性
    ),
    "google/gemini-2.5-pro": ModelConfig(
        name="google/gemini-2.5-pro",
        display_name="Gemini 2.5 Pro",
        category="google",
        max_tokens=4096,  # 保持较大的token数
        temperature=0.3,  # 降低随机性，提高一致性
    ),
    "deepseek/deepseek-chat": ModelConfig(
        name="deepseek/deepseek-chat",
        display_name="DeepSeek Chat",
        category="open_source"
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
    "meta-llama/llama-3.3-70b-instruct": ModelConfig(
        name="meta-llama/llama-3.3-70b-instruct",
        display_name="Llama 3.3 70B",
        category="open_source"
    ),
    "z-ai/glm-4.7": ModelConfig(
        name="z-ai/glm-4.7",
        display_name="GLM-4.7",
        category="open_source",
        max_tokens=2048,
        temperature=0.7
    ),
    "minimax/minimax-m2.1": ModelConfig(
        name="minimax/minimax-m2.1",
        display_name="Minimax M2.1",
        category="open_source",
        max_tokens=2048,
        temperature=0.7
    ),
}

# 默认的代码分析模型列表
DEFAULT_CODE_MODELS = [
    "openai/gpt-4o",
    "anthropic/claude-3-5-sonnet",
    "deepseek/deepseek-coder",
    "qwen/qwen-plus",
    "meta-llama/llama-3.3-70b-instruct",
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
    def compare_models(
        self, 
        code: str, 
        test_results: str, 
        model_list: Optional[List[str]] = None,
        parallel: bool = False,
        **kwargs
    ) -> Dict[str, ModelFeedbackResult]:
        """
        比较多个模型的反馈结果
        
        Args:
            code: 代码字符串
            test_results: 测试结果字符串
            model_list: 要比较的模型列表，如果为None则使用DEFAULT_CODE_MODELS
            parallel: 是否并行调用（当前版本暂不支持，保留接口）
            **kwargs: 传递给get_feedback的额外参数
            
        Returns:
            模型名称到反馈结果的字典
        """
        if model_list is None:
            model_list = DEFAULT_CODE_MODELS
        
        results = {}
        
        print(f"开始对比 {len(model_list)} 个模型...")
        for i, model_name in enumerate(model_list, 1):
            print(f"[{i}/{len(model_list)}] 正在调用模型: {model_name}")
            
            result = self.get_feedback(code, test_results, model_name, **kwargs)
            results[model_name] = result
            
            if result.status == "success":
                print(f"  ✓ 成功 ({result.response_time:.2f}s)")
            else:
                print(f"  ✗ 失败: {result.error_message}")
        
        return results

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

    def save_comparison_results(
        self, 
        results: Dict[str, ModelFeedbackResult], 
        output_file: str = "model_comparison.json"
    ):
        """
        保存对比结果到JSON文件
        
        Args:
            results: 对比结果字典
            output_file: 输出文件名
        """
        serializable_results = {}
        for model_name, result in results.items():
            result_dict = asdict(result)
            # 将dataclass转换为字典
            serializable_results[model_name] = result_dict
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(serializable_results, f, ensure_ascii=False, indent=2)
        
        print(f"对比结果已保存到: {output_file}")  

def get_llm_feedback_with_model(code: str, test_results: str, model_name: str) -> str:
    """兼容旧版本的函数"""
    client = LLMClient()
    result = client.get_feedback(code, test_results, model_name)
    if result.status == "success":
        return result.feedback
    else:
        raise Exception(f"模型调用失败: {result.error_message}")
def compare_models_on_single_sample(
code: str,
test_results: str,
model_list: Optional[List[str]] = None
) -> dict:
    """
    用同一份代码和测试结果，测试多个模型，返回对比结果
    Args:
        code: 代码字符串
        test_results: 测试结果字符串
        model_list: 要比较的模型列表

    Returns:
        对比结果字典
    """
    client = LLMClient()
    results = client.compare_models(code, test_results, model_list)
    # 转换为旧格式的字典
    legacy_results = {}
    for model_name, result in results.items():
        legacy_results[model_name] = {
            "feedback": result.feedback if result.status == "success" else f"调用失败: {result.error_message}",
            "status": result.status,
            "length": len(result.feedback) if result.status == "success" else 0,
            "response_time": result.response_time,
            "token_count": result.token_count
        }

    return legacy_results

if __name__ == "__main__":
    # 示例代码和测试结果
    sample_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)
'''
    sample_test_results = '''
测试用例1: fibonacci(0) -> 期望: 0, 实际: 0 ✓
测试用例2: fibonacci(1) -> 期望: 1, 实际: 1 ✓
测试用例3: fibonacci(5) -> 期望: 5, 实际: 5 ✓
测试用例4: fibonacci(10) -> 期望: 55, 实际: 55 ✓
所有测试通过！
'''
    # 创建客户端
    client = LLMClient()

    # 测试单个模型
    print("测试单个模型...")
    single_result = client.get_feedback(sample_code, sample_test_results, "deepseek/deepseek-coder")
    print(f"模型: {single_result.model_name}")
    print(f"状态: {single_result.status}")
    print(f"响应时间: {single_result.response_time:.2f}s")
    print(f"反馈长度: {len(single_result.feedback)} 字符")
    print("-" * 50)

    # 比较多个模型
    print("\n比较多个模型...")
    comparison_results = client.compare_models(
        sample_code, 
        sample_test_results,
        model_list=["deepseek/deepseek-coder", "openai/gpt-4o"],
        temperature=0.5,
        max_tokens=800
    )

    # 保存结果
    client.save_comparison_results(comparison_results)

    # 查看可用模型
    print("\n可用模型（编程专用）:")
    code_models = client.get_available_models(category="code_specialized")
    for model in code_models:
        print(f"  - {model.display_name} ({model.name})")