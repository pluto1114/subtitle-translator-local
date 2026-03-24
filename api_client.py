import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import json
import re
import subprocess
import time
import platform
import threading

class OllamaClient:
    def __init__(self, api_url, timeout=300, temperature=0.1, num_gpu=0):
        self.api_url = api_url
        self.timeout = timeout
        self.temperature = temperature
        self.num_gpu = num_gpu
        
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"]
        )
        
        self.session = requests.Session()
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,
            pool_maxsize=10
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        self._last_request_time = 0

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

    def start_ollama_service(self, progress_callback=None):
        if progress_callback:
            progress_callback("Starting Ollama service...")
        
        try:
            if platform.system() == "Windows":
                subprocess.Popen(
                    ["ollama", "serve"],
                    creationflags=subprocess.CREATE_NO_WINDOW | subprocess.DETACHED_PROCESS,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:
                subprocess.Popen(
                    ["ollama", "serve"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True
                )
            
            max_wait = 30
            for i in range(max_wait):
                time.sleep(1)
                if progress_callback:
                    progress_callback(f"Waiting for Ollama to start... ({i+1}/{max_wait}s)")
                if self.check_connection():
                    if progress_callback:
                        progress_callback("Ollama service started successfully!")
                    return True
            
            if progress_callback:
                progress_callback("Failed to start Ollama service within timeout.")
            return False
            
        except FileNotFoundError:
            if progress_callback:
                progress_callback("Error: 'ollama' command not found. Please install Ollama first.")
            return False
        except Exception as e:
            if progress_callback:
                progress_callback(f"Error starting Ollama: {str(e)}")
            return False

    def warm_up_model(self, model, progress_callback=None):
        max_attempts = 10
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            try:
                if progress_callback:
                    progress_callback(f"Loading model '{model}' (attempt {attempt}/{max_attempts})...")
                
                if "/v1/chat/completions" in self.api_url:
                    payload = {
                        "model": model,
                        "messages": [{"role": "user", "content": "Hi"}],
                        "stream": False,
                        "temperature": 0.1,
                        "think": False,
                        "num_gpu": self.num_gpu
                    }
                else:
                    payload = {
                        "model": model,
                        "prompt": "Hi",
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_gpu": self.num_gpu
                        },
                        "think": False
                    }
                
                headers = {"Content-Type": "application/json"}
                response = requests.post(self.api_url, json=payload, headers=headers, timeout=600)
                response.raise_for_status()
                
                if progress_callback:
                    progress_callback(f"Model '{model}' loaded successfully!")
                return True
                
            except requests.exceptions.Timeout:
                if progress_callback:
                    progress_callback(f"Model still loading... waiting (attempt {attempt}/{max_attempts})")
                time.sleep(5)
                continue
            except Exception as e:
                if progress_callback:
                    progress_callback(f"Error loading model: {str(e)}")
                time.sleep(3)
                continue
        
        return False

    def translate_batch(self, text, target_lang, model, count):
        system_prompt = f"""You are a professional subtitle translator. Translate the following numbered text blocks into {target_lang}.

You MUST output the translated blocks in the EXACT format below:

[1] first translation
[2] second translation
[3] third translation
...

Rules:
- Each block MUST start with [number] on a new line
- Do NOT include the original input text in your output
- Do NOT add explanations or extra content
- Do NOT change the order of the blocks
- Return exactly {count} numbered blocks in your response
- Output translation directly, no thinking tags

/no_think"""
        prompt = f"{text}"
        
        return self._make_request(model, system_prompt, prompt, is_batch=True)

    def translate_single(self, text, target_lang, model, max_retries=3):
        system_prompt = f"You are a professional subtitle translator. Translate the following text to {target_lang}. Keep it concise and suitable for subtitles. Do not output anything else. Do not output <think> tags. Translate directly. /no_think"
        prompt = f"{text}"
        
        last_exception = None
        for attempt in range(max_retries):
            try:
                result = self._make_request(model, system_prompt, prompt, is_batch=False)
                if result and len(result.strip()) > 0:
                    return result
            except Exception as e:
                last_exception = e
                if attempt < max_retries - 1:
                    time.sleep(attempt + 1)
        
        # If all retries failed, return original text
        print(f"Failed to translate single after {max_retries} attempts: {last_exception}")
        return text

    def _make_request(self, model, system_prompt, prompt, is_batch=False):
        if "/v1/chat/completions" in self.api_url:
            full_prompt = f"### System Prompt ###\n{system_prompt}\n\n### User Content ###\nText to translate:\n{prompt}"
            payload = {
                "model": model,
                "messages": [
                    {"role": "user", "content": full_prompt}
                ],
                "stream": False,
                "temperature": self.temperature,
                "num_gpu": self.num_gpu
            }
        else:
            payload = {
                "model": model,
                "prompt": prompt,
                "system": system_prompt,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_ctx": 8192 if is_batch else 2048,
                    "num_gpu": self.num_gpu
                },
                "think": False
            }

        headers = {"Content-Type": "application/json"}
        timeout = self.timeout * 2 if is_batch else self.timeout
        
        max_retries = 2
        last_exception = None
        
        for attempt in range(max_retries):
            try:
                self._last_request_time = time.time()
                
                response = self.session.post(
                    self.api_url, 
                    json=payload, 
                    headers=headers, 
                    timeout=timeout
                )
                response.raise_for_status()
                result = response.json()
                
                if "/v1/chat/completions" in self.api_url:
                    if 'choices' in result and len(result['choices']) > 0:
                        translated_text = result['choices'][0]['message']['content'].strip()
                    else:
                        raise Exception(f"Invalid API response: {str(result)[:100]}")
                else:
                    translated_text = result.get("response", "").strip()
                    if translated_text=="":
                        print(f"Empty response, result: {result}")
                        
                
                translated_text = re.sub(r'<think.*?>.*?</think\s*>', '', translated_text, flags=re.DOTALL).strip()
                return translated_text
                
            except requests.exceptions.ConnectionError as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = attempt + 1
                    time.sleep(wait_time)
                    continue
            except requests.exceptions.Timeout as e:
                last_exception = e
                if attempt < max_retries - 1:
                    wait_time = attempt + 1
                    time.sleep(wait_time)
                    continue
            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [429, 503]:
                    last_exception = e
                    if attempt < max_retries - 1:
                        wait_time = (attempt + 1) * 2
                        time.sleep(wait_time)
                        continue
                raise
            except Exception as e:
                last_exception = e
                break
        
        raise Exception(f"API Request Error after {max_retries} retries: {last_exception}")

    def list_models(self) -> list[str]:
        """获取已安装的 Ollama 模型列表
        
        Returns:
            list[str]: 模型名称列表，失败时返回空列表
        """
        try:
            parsed_url = requests.utils.urlparse(self.api_url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            tags_url = f"{base_url}/api/tags"
            
            response = requests.get(tags_url, timeout=5)
            response.raise_for_status()
            
            result = response.json()
            models = []
            if 'models' in result:
                for model in result['models']:
                    if 'name' in model:
                        models.append(model['name'])
            
            return sorted(models)
        except Exception:
            return []
