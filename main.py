import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
import threading
import concurrent.futures
import winsound
import re

from config import ConfigManager
from srt_processor import SRTProcessor
from api_client import OllamaClient

# Configure CustomTkinter
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class SubtitleTranslatorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Subtitle Translator Local")
        self.geometry("900x700")

        self.config_manager = ConfigManager()
        self.config = self.config_manager.load()

        self.files_to_translate = []
        self.target_languages = ["Chinese", "English", "Japanese", "Spanish", "French", "German", "Russian", "Korean", "Italian"]
        
        self.selected_target_language = ctk.StringVar(value=self.config["target_language"])
        self.model_name = ctk.StringVar(value=self.config["model"])
        self.output_directory = ctk.StringVar(value=self.config["output_directory"])
        self.use_original_filename = ctk.BooleanVar(value=False)
        self.is_translating = False
        self.loading_animation_running = False
        self.loading_animation_text = ""
        
        self.create_widgets()

    def create_widgets(self):
        # Main Container
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Title
        self.label_title = ctk.CTkLabel(self, text="Subtitle Translator Local", font=ctk.CTkFont(size=24, weight="bold"))
        self.label_title.grid(row=0, column=0, pady=20, sticky="ew")

        # Controls Frame
        self.frame_controls = ctk.CTkFrame(self)
        self.frame_controls.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.frame_controls.grid_columnconfigure(1, weight=1)

        # File Selection
        self.btn_select_files = ctk.CTkButton(self.frame_controls, text="Select .srt Files", command=self.select_files)
        self.btn_select_files.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.label_file_count = ctk.CTkLabel(self.frame_controls, text="No files selected")
        self.label_file_count.grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Selected Files List
        self.textbox_files = ctk.CTkTextbox(self.frame_controls, height=80)
        self.textbox_files.grid(row=1, column=0, columnspan=3, padx=10, pady=5, sticky="ew")
        self.textbox_files.configure(state="disabled")

        # Settings
        self.label_lang = ctk.CTkLabel(self.frame_controls, text="Target Language:")
        self.label_lang.grid(row=2, column=0, padx=10, pady=10, sticky="w")
        
        self.option_lang = ctk.CTkOptionMenu(self.frame_controls, variable=self.selected_target_language, values=self.target_languages)
        self.option_lang.grid(row=2, column=1, padx=10, pady=10, sticky="w")

        self.label_model = ctk.CTkLabel(self.frame_controls, text="Ollama Model:")
        self.label_model.grid(row=3, column=0, padx=10, pady=10, sticky="w")

        self.entry_model = ctk.CTkEntry(self.frame_controls, textvariable=self.model_name)
        self.entry_model.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Output Directory
        self.label_output = ctk.CTkLabel(self.frame_controls, text="Output Folder:")
        self.label_output.grid(row=4, column=0, padx=10, pady=10, sticky="w")

        self.entry_output = ctk.CTkEntry(self.frame_controls, textvariable=self.output_directory, placeholder_text="Default: Source folder")
        self.entry_output.grid(row=4, column=1, padx=10, pady=10, sticky="ew")

        self.btn_select_output = ctk.CTkButton(self.frame_controls, text="...", width=30, command=self.select_output_directory)
        self.btn_select_output.grid(row=4, column=2, padx=5, pady=10, sticky="w")

        # Checkbox for Original Filename
        self.check_filename = ctk.CTkCheckBox(self.frame_controls, text="Overwrite Original File (Keep Filename)", variable=self.use_original_filename)
        self.check_filename.grid(row=5, column=0, columnspan=2, padx=10, pady=10, sticky="w")

        self.btn_start = ctk.CTkButton(self.frame_controls, text="Start Translation", command=self.start_translation_thread, state="disabled", fg_color="green")
        self.btn_start.grid(row=6, column=0, columnspan=3, padx=10, pady=20, sticky="ew")

        # Progress Bar
        self.progressbar = ctk.CTkProgressBar(self.frame_controls)
        self.progressbar.grid(row=7, column=0, columnspan=2, padx=10, pady=10, sticky="ew")
        self.progressbar.set(0)
        
        self.label_progress_percent = ctk.CTkLabel(self.frame_controls, text="0%", width=60)
        self.label_progress_percent.grid(row=7, column=2, padx=10, pady=10, sticky="e")

        # Log Area
        self.textbox_log = ctk.CTkTextbox(self, width=800, height=250)
        self.textbox_log.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")
        self.textbox_log.configure(state="disabled")

    def select_files(self):
        filetypes = (("Subtitle files", "*.srt"), ("All files", "*.*"))
        filenames = filedialog.askopenfilenames(title="Select files", filetypes=filetypes)
        if filenames:
            self.files_to_translate = list(filenames)
            self.label_file_count.configure(text=f"{len(filenames)} files selected")
            
            # Update textbox
            self.textbox_files.configure(state="normal")
            self.textbox_files.delete("1.0", "end")
            for f in filenames:
                self.textbox_files.insert("end", os.path.basename(f) + "\n")
            self.textbox_files.configure(state="disabled")

            self.btn_start.configure(state="normal")
            self.log(f"Selected {len(filenames)} files.")

    def select_output_directory(self):
        directory = filedialog.askdirectory(title="Select Output Folder")
        if directory:
            self.output_directory.set(directory)
            self.log(f"Output directory set to: {directory}")
            self.save_current_config()

    def save_current_config(self):
        current_config = {
            "target_language": self.selected_target_language.get(),
            "model": self.model_name.get(),
            "output_directory": self.output_directory.get(),
            "batch_size": self.config.get("batch_size", 30),
            "max_workers": self.config.get("max_workers", 3),
            "ollama_api_url": self.config.get("ollama_api_url", "http://localhost:11434/api/generate"),
            "timeout": self.config.get("timeout", 300),
            "temperature": self.config.get("temperature", 0.1),
            "num_gpu": self.config.get("num_gpu", 0)
        }
        self.config_manager.save(current_config)
        self.config = current_config # Update in-memory config

    def log(self, message):
        self.after(0, self._log_internal, message)

    def _log_internal(self, message):
        self.textbox_log.configure(state="normal")
        self.textbox_log.insert("end", message + "\n")
        self.textbox_log.see("end")
        self.textbox_log.configure(state="disabled")

    def start_loading_animation(self, base_text):
        self.loading_animation_running = True
        self.loading_animation_text = base_text
        self._animate_loading()

    def stop_loading_animation(self):
        self.loading_animation_running = False

    def _animate_loading(self):
        if not self.loading_animation_running:
            return
        current_text = self.btn_start.cget("text")
        if "..." in current_text:
            new_text = current_text.replace("...", ".")
        elif current_text.endswith("."):
            dots = current_text.count(".") - current_text.rfind(".") + 1
            if dots >= 3:
                new_text = self.loading_animation_text + "..."
            else:
                new_text = current_text + "."
        else:
            new_text = self.loading_animation_text + "..."
        self.btn_start.configure(text=new_text)
        self.after(500, self._animate_loading)

    def start_translation_thread(self):
        if self.is_translating:
            return
        
        self.save_current_config()
        
        self.api_client = OllamaClient(
            self.config["ollama_api_url"], 
            self.config["timeout"],
            self.config["temperature"],
            self.config.get("num_gpu", 0)
        )

        self.is_translating = True
        self.btn_start.configure(state="disabled", text="Checking Connection...")
        self.btn_select_files.configure(state="disabled")
        self.btn_select_output.configure(state="disabled")
        self.progressbar.set(0)
        self.label_progress_percent.configure(text="0%")
        
        threading.Thread(target=self._initialize_and_translate, daemon=True).start()

    def _initialize_and_translate(self):
        model = self.model_name.get()
        
        self.start_loading_animation("Checking Ollama")
        self.log("Checking Ollama connection...")
        
        if not self.api_client.check_connection():
            self.log("Ollama service not running. Attempting to start...")
            self.start_loading_animation("Starting Ollama")
            
            if not self.api_client.start_ollama_service(self.log):
                self.stop_loading_animation()
                self.is_translating = False
                self.after(0, self.reset_ui)
                self.after(0, lambda: messagebox.showerror("Service Error", 
                    "Failed to start Ollama service.\n\n"
                    "Please ensure Ollama is installed and available in your PATH.\n"
                    "You can download it from: https://ollama.ai"))
                return
        
        self.start_loading_animation("Loading Model")
        self.log(f"Warming up model '{model}'...")
        
        if not self.api_client.warm_up_model(model, self.log):
            self.stop_loading_animation()
            self.is_translating = False
            self.after(0, self.reset_ui)
            self.after(0, lambda: messagebox.showerror("Model Error", 
                f"Failed to load model '{model}'.\n\n"
                "Please check if the model name is correct and Ollama has enough resources.\n"
                "You can pull a model using: ollama pull <model_name>"))
            return
        
        self.stop_loading_animation()
        self.log(f"Model '{model}' is ready. Starting translation...")
        self.after(0, lambda: self.btn_start.configure(text="Translating..."))
        
        self.translate_files()

    def translate_files(self):
        target_lang = self.selected_target_language.get()
        model = self.model_name.get()
        output_dir = self.output_directory.get()
        use_original_name = self.use_original_filename.get()
        max_workers = self.config.get("max_workers", 3)

        try:
            # Use ThreadPoolExecutor to translate files in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(self.translate_single_file, file_path, target_lang, model, output_dir, use_original_name): file_path 
                    for file_path in self.files_to_translate
                }
                
                for future in concurrent.futures.as_completed(futures):
                    file_path = futures[future]
                    try:
                        future.result()
                        self.log(f"Completed: {os.path.basename(file_path)}")
                    except Exception as e:
                        self.log(f"Error translating {os.path.basename(file_path)}: {str(e)}")
        finally:
            self.is_translating = False
            self.after(0, self.reset_ui)

    def reset_ui(self):
        self.stop_loading_animation()
        self.btn_start.configure(state="normal", text="Start Translation")
        self.btn_select_files.configure(state="normal")
        self.btn_select_output.configure(state="normal")
        self.progressbar.set(1.0)
        self.label_progress_percent.configure(text="100%")
        self.log("All tasks finished.")
        try:
            winsound.MessageBeep()
        except Exception:
            pass

    def update_progress(self, current, total, file_name=None):
        if total > 0:
            progress = current / total
            percent = int(progress * 100)
            self.after(0, lambda: self.progressbar.set(progress))
            self.after(0, lambda: self.label_progress_percent.configure(text=f"{percent}%"))
            if file_name:
                self.log(f"  [{file_name}] Progress: {current}/{total} ({percent}%)")

    def translate_single_file(self, file_path, target_lang, model, output_dir, use_original_name):
        self.log(f"Starting translation for: {os.path.basename(file_path)}")
        
        parsed_blocks = SRTProcessor.parse_srt(file_path)
        total_blocks = len(parsed_blocks)
        
        if total_blocks == 0:
            self.log(f"Warning: No valid SRT blocks found in {os.path.basename(file_path)}.")
            return

        batch_size = self.config.get("batch_size", 20)
        # Translate ALL blocks, not just "valid" ones
        all_indices = list(range(len(parsed_blocks)))
        
        max_workers = self.config.get("max_workers", 3)
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_batch = {}
            
            for i in range(0, len(all_indices), batch_size):
                batch_indices = all_indices[i:i+batch_size]
                batch_blocks = [parsed_blocks[idx] for idx in batch_indices]
                
                # Prepare batch text
                input_text = ""
                separator = "---BLOCK_SEP---"
                for i, b in enumerate(batch_blocks):
                    clean_text = b['text'].strip()
                    if len(clean_text) > 30:
                        clean_text = clean_text[:30]
                    input_text += f"{clean_text}"
                    if i < len(batch_blocks) - 1:
                        input_text += f"\n{separator}\n"
                
                future = executor.submit(self.process_batch, input_text, target_lang, model, batch_blocks)
                future_to_batch[future] = (i, batch_blocks)

            # Collect results as they complete
            total_batches = len(all_indices)
            processed_so_far = 0

            for future in concurrent.futures.as_completed(future_to_batch):
                i, batch_blocks = future_to_batch[future]
                try:
                    future.result()
                    processed_so_far += len(batch_blocks)
                    file_name = os.path.basename(file_path)
                    self.update_progress(processed_so_far, total_batches, file_name)
                except Exception as e:
                    self.log(f"Error processing batch in {os.path.basename(file_path)}: {e}")

        # Save new file
        base_name = os.path.basename(file_path)
        base, ext = os.path.splitext(base_name)
        
        if use_original_name:
            filename = f"{base}{ext}"
        else:
            filename = f"{base}_translated_{target_lang}{ext}"
            
        if output_dir and os.path.isdir(output_dir):
            new_file_path = os.path.join(output_dir, filename)
        else:
            # Default to same directory as source file
            source_dir = os.path.dirname(file_path)
            new_file_path = os.path.join(source_dir, filename)
        
        SRTProcessor.save_srt(new_file_path, parsed_blocks)
        self.log(f"Saved to: {new_file_path}")

    def process_batch(self, input_text, target_lang, model, batch_blocks):
        batch_start_idx = batch_blocks[0]['index'] if batch_blocks else "?"
        self.log(f"  Translating batch starting at index {batch_start_idx} ({len(batch_blocks)} blocks)...")
        
        try:
            translated_batch_text = self.api_client.translate_batch(input_text, target_lang, model, len(batch_blocks))
            
            preview_len = 500
            preview = translated_batch_text[:preview_len] + "..." if len(translated_batch_text) > preview_len else translated_batch_text
            # self.log(f"API response ({len(translated_batch_text)} chars): {preview.replace(chr(10), ' | ')}")
            
            parts = self._parse_batch_response(translated_batch_text, len(batch_blocks))
            
            self.log(f"Received {len(parts)} parts from API for {len(batch_blocks)} blocks. translated_batch_text: {len(translated_batch_text)}")
            
            for i, b in enumerate(batch_blocks):
                if i < len(parts) and parts[i]:
                    b['translated_text'] = parts[i]
                else:
                    self.log(f"Batch count mismatch or empty part. Fallback to single for block {b['index']}")
                    self.log(f"parts: {parts}, translated_batch_text: {translated_batch_text}, input_text: {input_text}")
                    try:
                        b['translated_text'] = self.api_client.translate_single(b['text'], target_lang, model)
                    except Exception as single_e:
                        self.log(f"Single translation also failed for block {b['index']}: {single_e}")
                        b['translated_text'] = b['text']
                        
        except Exception as e:
            self.log(f"Batch translation failed: {e}. Falling back to single translation.")
            for b in batch_blocks:
                try:
                    b['translated_text'] = self.api_client.translate_single(b['text'], target_lang, model)
                except Exception as single_e:
                    self.log(f"Single translation failed for block {b['index']}: {single_e}")
                    b['translated_text'] = b['text']
    
    def _parse_batch_response(self, response_text, expected_count):
        parts = []
        
        pattern = r'^\[(\d+)\]\s*'
        lines = response_text.split('\n')
        
        current_num = None
        current_text_lines = []
        
        for line in lines:
            match = re.match(pattern, line)
            if match:
                if current_num is not None:
                    parts.append('\n'.join(current_text_lines).strip())
                
                current_num = int(match.group(1))
                current_text_lines = [line[match.end():]]
            elif current_num is not None:
                current_text_lines.append(line)
        
        if current_num is not None:
            parts.append('\n'.join(current_text_lines).strip())
        
        if len(parts) == expected_count:
            return parts
        
        pattern2 = r'\[(\d+)\]\s*(.*?)(?=\n\s*\[\d+\]|$)'
        matches = re.findall(pattern2, response_text, re.DOTALL)
        if matches:
            translation_dict = {int(num): text.strip() for num, text in matches}
            parts = []
            for i in range(1, expected_count + 1):
                parts.append(translation_dict.get(i, ""))
            if len([p for p in parts if p]) > 0:
                return parts
        
        separator_pattern = r"---BLOCK_SEP---"
        if separator_pattern in response_text:
            parts = re.split(separator_pattern, response_text)
            parts = [p.strip() for p in parts if p.strip()]
            if len(parts) == expected_count:
                return parts
        
        lines_non_empty = [l.strip() for l in response_text.split('\n') if l.strip()]
        if len(lines_non_empty) == expected_count:
            return lines_non_empty
        
        if len(lines_non_empty) >= expected_count:
            return lines_non_empty[:expected_count]
        
        return parts

if __name__ == "__main__":
    app = SubtitleTranslatorApp()
    app.mainloop()
