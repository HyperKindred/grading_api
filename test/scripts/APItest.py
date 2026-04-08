import requests
import json

def test_minimal_request(model_id):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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", 
        "Content-Type": "application/json"
    }
    # 极简的请求体，只包含模型和消息
    payload = {
        "model": model_id,
        "messages": [
            {"role": "user", "content": "请回复‘你好’。"}
        ]
    }
    response = requests.post(url, headers=headers, json=payload)
    
    # 打印完整的响应，以便查看具体错误
    print(f"测试模型: {model_id}")
    print(f"状态码: {response.status_code}")
    print(f"响应体: {response.text}\n")
    return response

# 分别测试失败和成功的模型
test_minimal_request("google/gemini-2.5-pro") 
test_minimal_request("z-ai/glm-4.7")
test_minimal_request("minimax/minimax-m2.1") 
test_minimal_request("meta-llama/llama-3.3-70b-instruct")
