# 本地字幕翻译器 (Subtitle Translator Local)

**中文** | [English](README.md)

基于 Ollama 模型的本地字幕翻译工具。它允许你利用本地运行的大语言模型，将 `.srt` 字幕文件翻译成各种语言。

## 功能特点

*   **本地处理**：所有翻译均通过 Ollama 在本地完成，确保隐私安全且无 API 费用。
*   **批量处理**：支持多文件并发翻译，以及文件内的并发分块处理，最大化利用硬件性能。
*   **自定义模型**：支持 Ollama 中可用的任何模型（例如 Qwen, Llama3, Mistral, Sakura）。
*   **Prompt 优化**：针对字幕格式进行了 Prompt 工程优化，有效防止幻觉，并能抑制推理模型输出“思考过程”。
*   **鲁棒的错误处理**：如果批量翻译失败，会自动降级为逐行翻译模式，确保任务完成。
*   **智能分割**：使用特殊分隔符技术，完美支持多行字幕内容的翻译与解析。
*   **友好界面**：使用 CustomTkinter 构建，界面现代且易于操作。

## 前置要求

1.  **Python 3.8+**
2.  **Ollama**: 你必须安装并运行 [Ollama](https://ollama.com/)。
    *   从官网下载并安装 Ollama。
    *   拉取一个模型（例如：`ollama pull qwen2.5:7b`）。
    *   启动服务：`ollama serve`。

## 安装步骤

1.  克隆本仓库或下载源代码。
2.  安装所需的 Python 依赖包：

    ```bash
    pip install -r requirements.txt
    ```

    *注：如果你使用的是 Windows 系统，可以直接运行 `start_translator.bat`，它会自动检测环境并安装依赖。*

## 使用方法

1.  **启动 Ollama**：确保 Ollama 服务正在运行 (`ollama serve`)。
2.  **运行程序**：
    *   **Windows**: 双击 `start_translator.bat`。
    *   **手动**: 运行 `python main.py`。
3.  **配置任务**：
    *   **选择 .srt 文件**：选择一个或多个需要翻译的字幕文件。
    *   **目标语言**：选择你想要翻译成的语言。
    *   **Ollama 模型**：输入你在 Ollama 中拉取的模型名称（例如 `qwen2.5:7b` 或 `sakura-13b`）。
    *   **输出目录**：（可选）选择保存位置。留空则默认保存在源文件同级目录下。
4.  **开始翻译**：点击 "Start Translation" 按钮。

## 高级配置

程序首次运行后会自动生成 `config.json` 文件。你可以在此手动调整高级参数：

*   `max_workers`: 同时处理文件的并发线程数。
*   `batch_size`: 单次请求发送给模型的字幕块数量。
*   `timeout`: API 请求超时时间（秒）。
*   `temperature`: 模型生成的随机性 (0.0 - 1.0)。数值越低结果越确定。
*   `ollama_api_url`: Ollama API 的地址 (默认: `http://localhost:11434/api/generate`)。

## 常见问题排查

*   **连接错误**：请确保 Ollama 正在运行，且端口默认为 11434。
*   **翻译结果为空**：尝试更换一个指令遵循能力更强的模型，或者在 `config.json` 中降低 `temperature`。
*   **翻译速度慢**：尝试减小 `batch_size`，或者使用参数量更小/量化程度更高的模型。

## 许可证

MIT
