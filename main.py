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
        self.progressbar.grid(row=7, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.progressbar.set(0)

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
            "temperature": self.config.get("temperature", 0.1)
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

    def start_translation_thread(self):
        if self.is_translating:
            return
        
        self.save_current_config()
        
        # Init API Client
        self.api_client = OllamaClient(
            self.config["ollama_api_url"], 
            self.config["timeout"],
            self.config["temperature"]
        )

        # Check Ollama connection first
        if not self.api_client.check_connection():
            messagebox.showerror("连接错误", f"无法连接到 Ollama 服务。\n请确保 Ollama 已在本地启动，并且 API 地址配置正确。\n当前地址: {self.config['ollama_api_url']}")
            return
            
        self.is_translating = True
        self.btn_start.configure(state="disabled", text="Translating...")
        self.btn_select_files.configure(state="disabled")
        self.btn_select_output.configure(state="disabled")
        self.progressbar.set(0)
        
        threading.Thread(target=self.translate_files, daemon=True).start()

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
        self.btn_start.configure(state="normal", text="Start Translation")
        self.btn_select_files.configure(state="normal")
        self.btn_select_output.configure(state="normal")
        self.progressbar.set(1.0)
        self.log("All tasks finished.")
        # Play notification sound
        try:
            winsound.MessageBeep()
        except Exception:
            pass

    def update_progress(self, current, total):
        if total > 0:
            progress = current / total
            self.progressbar.set(progress)
            self.update_idletasks()

    def translate_single_file(self, file_path, target_lang, model, output_dir, use_original_name):
        self.log(f"Starting translation for: {os.path.basename(file_path)}")
        
        parsed_blocks = SRTProcessor.parse_srt(file_path)
        total_blocks = len(parsed_blocks)
        
        if total_blocks == 0:
            self.log(f"Warning: No valid SRT blocks found in {os.path.basename(file_path)}.")
            return

        batch_size = self.config.get("batch_size", 30)
        valid_indices = [i for i, b in enumerate(parsed_blocks) if b.get("is_valid", True)]
        
        # Process in batches using ThreadPoolExecutor for concurrent API calls within a single file
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.get("max_workers", 3)) as executor:
            future_to_batch = {}
            
            for i in range(0, len(valid_indices), batch_size):
                batch_indices = valid_indices[i:i+batch_size]
                batch_blocks = [parsed_blocks[idx] for idx in batch_indices]
                
                # Prepare batch text
                input_text = ""
                separator = "---BLOCK_SEP---"
                for i, b in enumerate(batch_blocks):
                    # Clean up text for prompt: replace newlines within a block with spaces to keep it as one line per block
                    clean_text = b['text'].strip()
                    input_text += f"{clean_text}"
                    if i < len(batch_blocks) - 1:
                        input_text += f"\n{separator}\n"
                
                future = executor.submit(self.process_batch, input_text, target_lang, model, batch_blocks)
                future_to_batch[future] = (i, batch_blocks)

            # Collect results as they complete
            total_batches = len(valid_indices)
            processed_so_far = 0

            for future in concurrent.futures.as_completed(future_to_batch):
                i, batch_blocks = future_to_batch[future]
                try:
                    future.result()
                    # Update progress
                    processed_so_far += len(batch_blocks)
                    self.update_progress(processed_so_far, total_batches)
                    
                    self.log(f"  [{os.path.basename(file_path)}] Processed batch starting at index {batch_blocks[0]['index']}")
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
        try:
            # Call API with batch
            translated_batch_text = self.api_client.translate_batch(input_text, target_lang, model, len(batch_blocks))
            
            # Split by separator instead of lines
            separator_pattern = r"---BLOCK_SEP---"
            parts = re.split(separator_pattern, translated_batch_text)
            # Filter out empty strings that might appear at start/end
            parts = [p.strip() for p in parts if p.strip()]
            
            # Assign translations based on order
            for i, b in enumerate(batch_blocks):
                if i < len(parts):
                    b['translated_text'] = parts[i]
                else:
                    # Fallback if counts mismatch
                    self.log(f"Batch count mismatch. Fallback to single for block {b['index']}")
                    b['translated_text'] = self.api_client.translate_single(b['text'], target_lang, model)
        except Exception as e:
            self.log(f"Batch translation failed: {e}. Falling back to single translation.")
            for b in batch_blocks:
                b['translated_text'] = self.api_client.translate_single(b['text'], target_lang, model)

if __name__ == "__main__":
    app = SubtitleTranslatorApp()
    app.mainloop()
