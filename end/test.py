import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")
print(f"API Key 前8位: {api_key[:8] if api_key else 'None'}")

if not api_key:
    print("❌ 未找到 API Key，请检查 .env 文件")
else:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek/deepseek-chat",
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 10
    }
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        print(f"状态码: {resp.status_code}")
        if resp.status_code == 200:
            print("✅ API 调用成功，网络和 Key 都正常")
        else:
            print(f"❌ API 返回错误: {resp.text}")
    except Exception as e:
        print(f"❌ 网络异常: {e}")