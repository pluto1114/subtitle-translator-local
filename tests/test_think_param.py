import requests
import json

# 测试think参数效果
model = "qwen3:8b"
api_url = "http://localhost:11434/api/generate"

print(f"测试模型: {model}")
print(f"API URL: {api_url}")
print("=" * 60)

# 测试1: think=False
print("\n[测试1] think=False")
payload1 = {
    "model": model,
    "prompt": "Hello world",
    "system": "Translate to Chinese",
    "stream": False,
    "think": False,
    "options": {"temperature": 0.1}
}

try:
    response = requests.post(api_url, json=payload1, headers={"Content-Type": "application/json"}, timeout=30)
    if response.status_code == 200:
        result = response.json()
        text = result.get('response', '')
        print(f"响应内容: {repr(text)}")
        has_think = '<think' in text.lower() or '</think' in text.lower()
        print(f"是否包含think标签: {has_think}")
        print(f"完整响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"异常: {e}")

print("\n" + "=" * 60)

# 测试2: 使用api_client.py中的translate_single
print("\n[测试2] 使用api_client.py中的translate_single (think=False)")
from api_client import OllamaClient

client = OllamaClient(api_url, timeout=120, temperature=0.1)
try:
    result = client.translate_single("Hello world", "Chinese", model)
    print(f"translate_single结果: {repr(result)}")
    has_think = '<think' in result.lower() or '</think' in result.lower()
    print(f"是否包含think标签: {has_think}")
except Exception as e:
    print(f"异常: {e}")