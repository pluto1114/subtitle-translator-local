from api_client import OllamaClient

# 测试 API 客户端
api_url = "http://localhost:11434/api/generate"
client = OllamaClient(api_url, timeout=120, temperature=0.7)

print("检查连接...")
if client.check_connection():
    print("连接成功!")
else:
    print("连接失败!")

print("\n预热模型 qwen3.5:9b...")

def progress_callback(message):
    print(f"  {message}")

result = client.warm_up_model("qwen3.5:9b", progress_callback)
if result:
    print("模型预热成功!")
else:
    print("模型预热失败!")