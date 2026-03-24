# Ollama Model 下拉列表功能

## 1. 功能概述

将现有的 "Ollama Model" 文本输入框改为下拉选择列表，自动显示用户已安装的所有 Ollama 模型，提高用户体验。

## 2. 需求分析

### 2.1 当前状态
- 模型名称通过文本输入框输入
- 用户需要手动输入正确的模型名称
- 容易出现拼写错误

### 2.2 改进需求
- 自动获取并显示已安装的模型列表
- 通过下拉菜单选择模型
- 保持原有的配置保存功能

## 3. 技术实现方案

### 3.1 方案概述
- 在 `api_client.py` 中新增获取已安装模型列表的方法
- 使用 Ollama 的 API 接口 `/api/tags` 获取模型列表
- 在 `main.py` 中将 `CTkEntry` 改为 `CTkOptionMenu`
- 应用启动时自动加载模型列表

### 3.2 具体实现

#### 3.2.1 OllamaClient 新增方法 `list_models()`
- 调用 Ollama 的 `/api/tags` 接口
- 解析返回的 JSON 数据
- 返回模型名称列表

#### 3.2.2 UI 组件变更
- 移除 `self.entry_model` (CTkEntry)
- 新增 `self.option_model` (CTkOptionMenu)
- 绑定到现有的 `self.model_name` 变量
- 在应用初始化时调用 `load_installed_models()` 加载模型列表

#### 3.2.3 错误处理
- 如果获取模型列表失败，显示默认值或空列表
- 保持原有的手动输入作为备用选项（可选）

## 4. 接口设计

### 4.1 OllamaClient.list_models()
```python
def list_models(self) -> list[str]:
    """获取已安装的 Ollama 模型列表
    
    Returns:
        list[str]: 模型名称列表，失败时返回空列表
    """
```

### 4.2 新的 UI 组件
```python
self.option_model = ctk.CTkOptionMenu(
    self.frame_controls, 
    variable=self.model_name,
    values=[]  # 初始为空，加载后更新
)
```

## 5. 实现步骤

1. 在 `api_client.py` 中实现 `list_models()` 方法
2. 在 `main.py` 的 `__init__` 中调用 `load_installed_models()` 方法
3. 将 `CTkEntry` 替换为 `CTkOptionMenu`
4. 实现加载和更新下拉列表的逻辑
5. 测试功能

## 6. 注意事项

- 保持向后兼容性：如果用户之前保存了配置，依然可以正常加载
- 错误处理：如果 Ollama 未运行，模型列表可能为空
- 性能：获取模型列表应该在后台线程中进行，避免阻塞 UI
