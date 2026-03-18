import requests
import json
from api_client import OllamaClient
from config import ConfigManager

# 测试 num_gpu 配置
print("=" * 60)
print("测试 num_gpu 配置")
print("=" * 60)

# 1. 测试 ConfigManager
print("\n[1] 测试 ConfigManager")
config_manager = ConfigManager()
config = config_manager.load()
print(f"加载的配置: {json.dumps(config, ensure_ascii=False, indent=2)}")
print(f"num_gpu 值: {config.get('num_gpu')}")

# 2. 测试 OllamaClient 初始化
print("\n[2] 测试 OllamaClient 初始化")
api_url = config["ollama_api_url"]
client = OllamaClient(
    api_url, 
    timeout=config["timeout"], 
    temperature=config["temperature"],
    num_gpu=config["num_gpu"]
)
print(f"OllamaClient 初始化成功")
print(f"client.num_gpu = {client.num_gpu}")

# 3. 测试连接
print("\n[3] 测试 Ollama 连接")
if client.check_connection():
    print("连接成功!")
else:
    print("连接失败!")
    exit(1)

# 4. 测试带 num_gpu 的请求
print("\n[4] 测试带 num_gpu 的翻译请求")
try:
    result = client.translate_single("Hello world", "Chinese", config["model"])
    print(f"翻译结果: {repr(result)}")
    print("测试成功!")
except Exception as e:
    print(f"测试失败: {e}")

print("\n" + "=" * 60)
print("测试完成!")
print("=" * 60)