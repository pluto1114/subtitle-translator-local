import requests

print("检查 Ollama API 状态...")

# 检查 Ollama 是否运行
try:
    response = requests.get("http://localhost:11434/api/tags")
    print(f"Ollama 服务状态: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        models = data.get('models', [])
        if models:
            print(f"\n已安装的模型:")
            for model in models:
                print(f"  - {model['name']} ({model['size']/1024/1024/1024:.2f} GB)")
        else:
            print("\n⚠️  Ollama 中没有安装任何模型！")
except Exception as e:
    print(f"❌ 无法连接到 Ollama: {e}")
    print("请确保 Ollama 服务正在运行 (ollama serve)")
