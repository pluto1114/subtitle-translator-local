import requests
import json

# 测试 qwen3:8b 模型
model = "qwen3:8b"
api_url = "http://localhost:11434/api/generate"

print(f"测试模型: {model}")
print(f"API URL: {api_url}")

payload = {
    "model": model,
    "prompt": "Hello, how are you?",
    "stream": False,
    "options": {"temperature": 0.1}
}

headers = {"Content-Type": "application/json"}

try:
    print("发送请求...")
    response = requests.post(api_url, json=payload, headers=headers, timeout=30)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"响应: {result.get('response', '无响应内容')[:150]}...")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"异常: {e}")