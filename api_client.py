import requests
import json
import re

class OllamaClient:
    def __init__(self, api_url, timeout=300, temperature=0.1):
        self.api_url = api_url
        self.timeout = timeout
        self.temperature = temperature

    def check_connection(self):
        try:
            parsed_url = requests.utils.urlparse(self.api_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            try:
                requests.get(base_url, timeout=2)
                return True
            except:
                response = requests.get(self.api_url, timeout=2)
                if response.status_code in [200, 404, 405]:
                    return True
                return False
        except:
            return False

    def translate_batch(self, text, target_lang, model, count):
        separator = "---BLOCK_SEP---"
        system_prompt = (
            f"You are a professional subtitle translator. Translate the following text blocks into {target_lang}. "
            f"The input blocks are separated by '{separator}'. "
            f"You MUST output the translated blocks separated by exactly the same separator '{separator}'. "
            f"Do not include original text. Do not add explanations. "
            f"IMPORTANT: Disable deep thinking. Do not generate <think> tags. Output translation directly. "
            f"Return exactly {count} blocks. /no_think"
        )
        prompt = f"{text}"
        
        return self._make_request(model, system_prompt, prompt, is_batch=True)

    def translate_single(self, text, target_lang, model):
        system_prompt = f"You are a professional subtitle translator. Translate the following text to {target_lang}. Keep it concise and suitable for subtitles. Do not output anything else. Do not output <think> tags. Translate directly. /no_think"
        prompt = f"{text}"
        return self._make_request(model, system_prompt, prompt, is_batch=False)

    def _make_request(self, model, system_prompt, prompt, is_batch=False):
        if "/v1/chat/completions" in self.api_url:
            full_prompt = f"### System Prompt ###\n{system_prompt}\n\n### User Content ###\nText to translate:\n{prompt}"
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "stream": False,
                "temperature": self.temperature
            }
        else:
            payload = {
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_ctx": 4096 if is_batch else 2048
                }
            }

        headers = {"Content-Type": "application/json"}
        timeout = self.timeout * 2 if is_batch else self.timeout
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            result = response.json()
            
            if "/v1/chat/completions" in self.api_url:
                if 'choices' in result and len(result['choices']) > 0:
                    translated_text = result['choices'][0]['message']['content'].strip()
                else:
                    raise Exception(f"Invalid API response: {str(result)[:100]}")
            else:
                translated_text = result.get("response", "").strip()
            
            # Remove <think> tags
            translated_text = re.sub(r'<think>.*?</think>', '', translated_text, flags=re.DOTALL).strip()
            return translated_text
        except Exception as e:
            raise Exception(f"API Request Error: {e}")
