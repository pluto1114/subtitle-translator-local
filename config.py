import json
import os

class ConfigManager:
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.defaults = {
            "target_language": "Chinese",
            "model": "qwen3:8b",
            "output_directory": "",
            "batch_size": 30,
            "max_workers": 3,
            "ollama_api_url": "http://localhost:11434/api/generate",
            "timeout": 300,
            "temperature": 0.1
        }
        self.config = self.defaults.copy()

    def load(self):
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Update self.config with loaded values, keeping defaults for missing keys
                    for key in self.defaults:
                        if key in loaded_config:
                            self.config[key] = loaded_config[key]
            except Exception as e:
                print(f"Error loading config: {e}")
        return self.config

    def save(self, current_config):
        # current_config should be a dict with keys matching defaults
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(current_config, f, indent=4)
        except Exception as e:
            print(f"Error saving config: {e}")

    def get(self, key):
        return self.config.get(key, self.defaults.get(key))
