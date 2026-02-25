# Subtitle Translator Local

[中文版](README_CN.md) | **English**

A local subtitle translation tool powered by Ollama models. It allows you to translate `.srt` subtitle files into various languages using large language models running locally on your machine.

## Features

*   **Local Processing**: All translations are performed locally using Ollama, ensuring privacy and no API costs.
*   **Batch Processing**: Supports concurrent translation of multiple files and concurrent processing within files for maximum speed.
*   **Customizable Models**: Works with any model available in Ollama (e.g., Qwen, Llama3, Mistral).
*   **Prompt Engineering**: Optimized prompts to handle subtitle formats, prevent hallucinations, and suppress "thinking" output from reasoning models.
*   **Robust Error Handling**: Automatically falls back to single-line translation if batch translation fails.
*   **Smart Splitting**: Uses special separators to handle multi-line subtitles correctly.
*   **User-Friendly GUI**: Built with CustomTkinter for a modern and easy-to-use interface.

## Prerequisites

1.  **Python 3.8+**
2.  **Ollama**: You must have [Ollama](https://ollama.com/) installed and running.
    *   Install Ollama from their official website.
    *   Pull a model (e.g., `ollama pull qwen2.5:7b`).
    *   Start the server: `ollama serve`.

## Installation

1.  Clone this repository or download the source code.
2.  Install the required Python packages:

    ```bash
    pip install -r requirements.txt
    ```

    *Note: If you are on Windows, you can simply run `start_translator.bat` which will handle dependency installation for you.*

## Usage

1.  **Start Ollama**: Ensure Ollama is running (`ollama serve`).
2.  **Run the App**:
    *   **Windows**: Double-click `start_translator.bat`.
    *   **Manual**: Run `python main.py`.
3.  **Configure**:
    *   **Select .srt Files**: Choose one or more subtitle files to translate.
    *   **Target Language**: Select the language you want to translate into.
    *   **Ollama Model**: Enter the name of the model you pulled in Ollama (e.g., `qwen2.5:7b`, `sakura-13b`).
    *   **Output Folder**: (Optional) Select a destination folder. If left empty, files are saved in the source directory.
4.  **Translate**: Click "Start Translation".

## Configuration

The application automatically creates a `config.json` file after the first run. You can manually tweak advanced settings here:

*   `max_workers`: Number of concurrent threads for file processing.
*   `batch_size`: Number of subtitle blocks sent to the model in a single request.
*   `timeout`: API request timeout in seconds.
*   `temperature`: Model creativity (0.0 - 1.0). Lower is more deterministic.
*   `ollama_api_url`: URL of the Ollama API (default: `http://localhost:11434/api/generate`).

## Troubleshooting

*   **Connection Error**: Make sure Ollama is running on port 11434.
*   **Empty Translation**: Try using a different model or lowering the `temperature` in `config.json`.
*   **Slow Translation**: Reduce `batch_size` or use a smaller/quantized model.

## License

MIT
