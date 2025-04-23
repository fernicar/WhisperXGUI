import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog, messagebox
import threading
import whisperx
import os
import sys
import datetime
import shutil
from pathlib import Path
import queue
import torch
import platform
import subprocess
import importlib
import threading
import time
import sys

# Lightning automatically upgraded your loaded checkpoint from v1.5.4 to v2.5.1. To apply the upgrade to your files permanently, run
# `python -m pytorch_lightning.utilities.upgrade_checkpoint G:\WhisperXGUI\.venv\Lib\site-packages\whisperx\assets\pytorch_model.bin`

class SplashScreen(tk.Toplevel):
    def __init__(self):
        super().__init__()

        # Remove window decorations
        self.overrideredirect(True)

        # Get screen dimensions
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Set window dimensions and position
        width = 300
        height = 200
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        # Configure the window
        self.configure(bg='#2d2d2d')

        # Create and pack widgets
        title = tk.Label(
            self,
            text="WhisperX GUI",
            font=("Helvetica", 16, "bold"),
            bg='#2d2d2d',
            fg='white'
        )
        title.pack(pady=(20, 10))

        loading_text = tk.Label(
            self,
            text="Loading dependencies...",
            font=("Helvetica", 10),
            bg='#2d2d2d',
            fg='white'
        )
        loading_text.pack(pady=5)

        # Create a progress bar
        self.progress = ttk.Progressbar(
            self,
            mode='indeterminate',
            length=200
        )
        self.progress.pack(pady=10)

        # Start progress bar animation
        self.progress.start()

        # Keep track of loaded modules
        self.status_label = tk.Label(
            self,
            text="",
            font=("Helvetica", 8),
            bg='#2d2d2d',
            fg='#a0a0a0',
            wraplength=280
        )
        self.status_label.pack(pady=5)

        # Center the window
        self.update_idletasks()

        # Make this window stay on top
        self.attributes('-topmost', True)

    def update_status(self, text):
        self.status_label.config(text=text)
        self.update()

def import_with_status(splash_screen):
    """Import all required modules while updating the splash screen"""

    modules_to_import = [
        ('tkinter.scrolledtext', 'GUI Components'),
        ('tkinter.filedialog', 'File Dialog'),
        ('tkinter.messagebox', 'Message Boxes'),
        ('whisperx', 'WhisperX Core'),
        ('torch', 'PyTorch'),
        ('datetime', 'DateTime Utils'),
        ('pathlib', 'Path Utils'),
        ('queue', 'Threading Queue'),
        ('platform', 'Platform Utils'),
        ('subprocess', 'Subprocess Utils')
    ]

    imported_modules = {}

    for module_name, display_name in modules_to_import:
        splash_screen.update_status(f"Loading {display_name}...")
        try:
            imported_modules[module_name] = importlib.import_module(module_name)
            time.sleep(0.1)  # Give a small delay to show the loading message
        except ImportError as e:
            splash_screen.update_status(f"Error loading {display_name}: {str(e)}")
            time.sleep(2)
            sys.exit(1)

    return imported_modules


# Here's where we define our WhisperXGUI class with all the imported modules
class WhisperXGUI:
    def __init__(self, root, modules):
        self.root = root
        self.root.title("WhisperX Transcription GUI")
        self.root.geometry("800x600")

        # Unpack needed modules
        self.scrolledtext = modules['tkinter.scrolledtext']
        self.filedialog = modules['tkinter.filedialog']
        self.messagebox = modules['tkinter.messagebox']
        self.whisperx = modules['whisperx']
        self.torch = modules['torch']
        self.Path = modules['pathlib'].Path
        self.queue = modules['queue'].Queue
        self.platform = modules['platform']
        self.subprocess = modules['subprocess']

        # Queue for communication between threads
        self.output_queue = self.queue()

        # List to store multiple file paths
        self.file_list = []

        self.setup_ui()
        self.setup_bindings()

        # Start the output checking loop
        self.check_output()

    def setup_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # File selection
        ttk.Label(main_frame, text="Input Files:").grid(row=0, column=0, sticky=tk.W)
        self.files_listbox = tk.Listbox(main_frame, width=50, height=5)
        self.files_listbox.grid(row=0, column=1, padx=5, sticky=(tk.W, tk.E))

        # File buttons frame
        file_buttons_frame = ttk.Frame(main_frame)
        file_buttons_frame.grid(row=0, column=2, padx=5)

        ttk.Button(file_buttons_frame, text="➕ Add Files", command=self.browse_files).grid(row=0, column=0, pady=2)
        ttk.Button(file_buttons_frame, text="➖ Remove Selected", command=self.remove_selected_file).grid(row=1, column=0, pady=2)
        ttk.Button(file_buttons_frame, text="🆑 Clear All", command=self.clear_files).grid(row=2, column=0, pady=2)

        # Model selection
        ttk.Label(main_frame, text="Model:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.model_var = tk.StringVar(value="medium")
        models = ["tiny", "base", "small", "medium", "large-v2"]
        model_combo = ttk.Combobox(main_frame, textvariable=self.model_var, values=models, state="readonly")
        model_combo.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=5)

        # Language selection with full names
        ttk.Label(main_frame, text="Language:").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.language_mapping = {
            "English": "en",
            "French": "fr",
            "German": "de",
            "Spanish": "es",
            "Italian": "it",
            "Japanese": "ja",
            "Chinese": "zh",
            "Dutch": "nl",
            "Ukrainian": "uk",
            "Portuguese": "pt"
        }
        self.language_var = tk.StringVar(value="English")
        language_names = list(self.language_mapping.keys())
        language_combo = ttk.Combobox(main_frame, textvariable=self.language_var, values=language_names, state="readonly")
        language_combo.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=5)

        # Compute type selection
        ttk.Label(main_frame, text="Compute Type:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.compute_type_var = tk.StringVar(value="float16")
        compute_types = ["float32", "float16", "int8"]
        compute_type_combo = ttk.Combobox(main_frame, textvariable=self.compute_type_var, values=compute_types, state="readonly")
        compute_type_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5)

        # Word timestamps checkbox
        self.word_timestamps_var = tk.BooleanVar(value=False)
        word_timestamps_check = ttk.Checkbutton(main_frame, text="Enable word-level timestamps", variable=self.word_timestamps_var)
        word_timestamps_check.grid(row=3, column=2, sticky=tk.W, pady=5)

        # Progress and output
        self.output_text = scrolledtext.ScrolledText(main_frame, height=20, width=70, wrap=tk.WORD)
        self.output_text.grid(row=4, column=0, columnspan=3, pady=10)
        self.output_text.config(state='disabled')

        # Transcribe button
        self.transcribe_btn = ttk.Button(main_frame, text="✨ Transcribe All", command=self.start_transcription)
        self.transcribe_btn.grid(row=5, column=0, columnspan=3, pady=10)

        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

    def browse_files(self):
        filetypes = (
            ("Video/audio", "*.mp4 *.mkv *.mov *.wmv *.avi *.flv *.mp3 *.wav *.aac *.flac *.ogg *.m4a"),
            ("Video", "*.mp4 *.mkv *.mov *.wmv *.avi *.flv"),
            ("Audio", "*.mp3 *.wav *.aac *.flac *.ogg *.m4a"),
            ("All files", "*.*")
        )
        filenames = filedialog.askopenfilenames(filetypes=filetypes)
        if filenames:
            for filename in filenames:
                if filename not in self.file_list:
                    self.file_list.append(filename)
                    self.files_listbox.insert(tk.END, os.path.basename(filename))

    def remove_selected_file(self):
        selection = self.files_listbox.curselection()
        if selection:
            index = selection[0]
            self.files_listbox.delete(index)
            self.file_list.pop(index)

    def clear_files(self):
        self.files_listbox.delete(0, tk.END)
        self.file_list.clear()

    def setup_bindings(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_output(self, message):
        self.output_text.config(state='normal')
        self.output_text.insert(tk.END, message + '\n')
        self.output_text.see(tk.END)
        self.output_text.config(state='disabled')

    def check_output(self):
        try:
            while True:
                message = self.output_queue.get_nowait()
                self.update_output(message)
        except queue.Empty:
            pass
        finally:
            self.root.after(100, self.check_output)

    def create_output_directory(self, input_file):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
        base_name = Path(input_file).stem
        output_dir = Path("transcripts") / f"{base_name}_{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def transcribe(self, batch_size=16, language="en"):
        try:
            if not self.file_list:
                messagebox.showerror("Error", "Please select at least one input file")
                return

            device = "cuda" if torch.cuda.is_available() else "cpu"
            compute_type = self.compute_type_var.get()
            selected_language = self.language_var.get()
            if selected_language != "English":
                self.output_queue.put(f"Using other language: {selected_language}")
                language = self.language_mapping[selected_language]
            else:
                self.output_queue.put(f"Using language: {selected_language}")

            # Load model once for all files
            self.output_queue.put("Loading WhisperX model...")
            model = whisperx.load_model(
                self.model_var.get(),
                device,
                compute_type=compute_type
            )

            for input_file in self.file_list:
                self.output_queue.put(f"\nStarting transcription of: {input_file}")

                # Create output directory
                output_dir = self.create_output_directory(input_file)
                self.output_queue.put(f"Output directory: {output_dir}")

                # Load audio
                audio = whisperx.load_audio(input_file)

                # Transcribe
                word_timestamps = self.word_timestamps_var.get()
                self.output_queue.put(f"Transcribing... (Word timestamps: {'enabled' if word_timestamps else 'disabled'})")

                # WhisperX handles word timestamps differently
                # First transcribe with Whisper (without word timestamps parameter)
                self.output_queue.put("Transcribing with WhisperX...")
                result = model.transcribe(audio, batch_size=batch_size, language=language)

                # Word timestamps will be added in the alignment step

                # Align
                self.output_queue.put("Aligning transcript...")
                model_a, metadata = whisperx.load_align_model(
                    language_code=language,
                    device=device
                )
                # In WhisperX, the align function is where word-level timestamps are generated
                self.output_queue.put(f"Aligning with word timestamps: {'enabled' if word_timestamps else 'disabled'}")

                # WhisperX align function doesn't have a return_word_timestamps parameter
                # It always returns word timestamps when available
                result = whisperx.align(
                    result["segments"],
                    model_a,
                    metadata,
                    audio,
                    device,
                    return_char_alignments=False
                )

                # Save output files
                srt_path = output_dir / f"{Path(input_file).stem}.srt"
                txt_path = output_dir / f"{Path(input_file).stem}.txt"

                # Write SRT file
                with open(srt_path, 'w', encoding='utf-8') as f:
                    for i, seg in enumerate(result["segments"], 1):
                        start = self.format_timestamp(seg["start"])
                        end = self.format_timestamp(seg["end"])
                        text = seg['text'].strip()

                        # If word timestamps are enabled and words are available, highlight them
                        if word_timestamps and 'words' in seg:
                            highlighted_text = ""
                            for word in seg['words']:
                                word_text = word['word']
                                highlighted_text += f"<font color=\"#ff0000\">{word_text}</font> "
                            if highlighted_text:
                                text = highlighted_text.strip()

                        f.write(f"{i}\n{start} --> {end}\n{text}\n\n")

                # Write TXT file
                with open(txt_path, 'w', encoding='utf-8') as f:
                    for seg in result["segments"]:
                        f.write(f"{seg['text'].strip()}\n")

                self.output_queue.put(f"Transcription complete for: {input_file}")
                self.output_queue.put(f"Files saved in: {output_dir}")

                # Open the output directory
                self.open_folder(output_dir)

                # Clean up alignment model
                del model_a
                torch.cuda.empty_cache()

            # Clean up whisper model
            del model
            torch.cuda.empty_cache()

            self.output_queue.put("\nAll files processed successfully!")

        except Exception as e:
            self.output_queue.put(f"Error during transcription: {str(e)}")
            messagebox.showerror("Error", f"Transcription failed: {str(e)}")
        finally:
            self.transcribe_btn.config(state='normal')

    def open_folder(self, path):
        path = os.path.realpath(path)
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(["open", path])
        else:  # Linux
            subprocess.run(["xdg-open", path])

    def format_timestamp(self, seconds):
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds % 1) * 1000)
        seconds = int(seconds)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def start_transcription(self):
        self.transcribe_btn.config(state='disabled')
        threading.Thread(target=self.transcribe, daemon=True).start()

    def on_closing(self):
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.root.quit()


# Function to finish initialization and show main window
def finish_init():
    # Create the application instance (stored as a global variable to prevent garbage collection)
    global app
    app = WhisperXGUI(root, imported_modules)
    root.deiconify()  # Show the main window
    splash.destroy()   # Close the splash screen


if __name__ == "__main__":
    # Create and show the splash screen
    root = tk.Tk()
    root.withdraw()  # Hide the main window initially
    splash = SplashScreen()

    # Import dependencies
    imported_modules = import_with_status(splash)

    # Now import our WhisperXGUI class and global variables
    splash.update_status("Initializing application...")

    # Schedule the final initialization
    root.after(1000, finish_init)

    # Start the main loop
    root.mainloop()