import requests
import json
import time
import subprocess

# 测试 GPU 使用
model = "qwen3.5:9b"
api_url = "http://localhost:11434/api/generate"

print("测试 GPU 使用情况...")
print(f"模型: {model}")

# 先检查当前 GPU 使用率
print("\n当前 GPU 状态:")
subprocess.run(["nvidia-smi"], shell=True)

# 发送请求
payload = {
    "model": model,
    "prompt": "Write a short story about AI and humans",
    "stream": False,
    "options": {
        "temperature": 0.7,
        "num_thread": 4
    }
}

headers = {"Content-Type": "application/json"}

try:
    print("\n发送请求...")
    start_time = time.time()
    
    # 在后台监控 GPU 使用率
    def monitor_gpu():
        for i in range(5):
            time.sleep(2)
            print(f"\nGPU 使用率 ({i+1}/5):")
            subprocess.run(["nvidia-smi", "--query-gpu=utilization.gpu,memory.used", "--format=csv,noheader"], shell=True)
    
    import threading
    monitor_thread = threading.Thread(target=monitor_gpu)
    monitor_thread.daemon = True
    monitor_thread.start()
    
    response = requests.post(api_url, json=payload, headers=headers, timeout=120)
    end_time = time.time()
    
    print(f"\n请求耗时: {end_time - start_time:.2f}秒")
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"响应长度: {len(result.get('response', ''))} 字符")
        print(f"前 100 字符: {result.get('response', '')[:100]}...")
    else:
        print(f"错误: {response.text}")
except Exception as e:
    print(f"异常: {e}")