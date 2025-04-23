import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import re
import os
import threading
import time
import subprocess
from pathlib import Path
from datetime import datetime
import pygame

class SRTVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT Word Timestamp Visualizer")
        self.root.geometry("800x600")

        # Initialize pygame mixer for audio playback
        pygame.mixer.init()

        # Variables
        self.srt_file = None
        self.audio_file = None
        self.words = []  # List of (word, start_time, end_time) tuples
        self.playing = False
        self.current_time = 0
        self.start_time = 0

        # Create UI
        self.create_ui()

    def create_ui(self):
        # Frame for file selection
        file_frame = ttk.Frame(self.root, padding="10")
        file_frame.pack(fill=tk.X)

        # SRT file selection
        ttk.Label(file_frame, text="SRT File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.srt_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.srt_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_srt).grid(row=0, column=2, padx=5, pady=5)

        # Audio file selection
        ttk.Label(file_frame, text="Audio File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.audio_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.audio_path_var, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(file_frame, text="Browse", command=self.browse_audio).grid(row=1, column=2, padx=5, pady=5)

        # Load button
        ttk.Button(file_frame, text="Load Files", command=self.load_files).grid(row=2, column=1, padx=5, pady=10)

        # Playback controls - with more visible styling at the top
        control_frame = ttk.Frame(self.root, padding="15")
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        # Create a more prominent play button with custom styling
        style = ttk.Style()
        style.configure('Play.TButton', font=('Arial', 12, 'bold'))
        style.configure('Stop.TButton', font=('Arial', 12, 'bold'))

        self.play_button = ttk.Button(control_frame, text="▶ Play Audio", command=self.toggle_playback,
                                    width=15, style='Play.TButton')
        self.play_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.play_button.config(state=tk.DISABLED)  # Disabled until files are loaded

        self.stop_button = ttk.Button(control_frame, text="⏹ Stop", command=self.stop_playback,
                                     width=10, style='Stop.TButton')
        self.stop_button.pack(side=tk.LEFT, padx=10, pady=5)
        self.stop_button.config(state=tk.DISABLED)  # Disabled until files are loaded

        # Time display
        self.time_var = tk.StringVar(value="00:00:00.000")
        ttk.Label(control_frame, textvariable=self.time_var).pack(side=tk.RIGHT, padx=5)

        # Progress bar
        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Scale(control_frame, orient=tk.HORIZONTAL, variable=self.progress_var,
                                      from_=0, to=100, command=self.seek)
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Add a separator below the controls for better visibility
        ttk.Separator(self.root, orient='horizontal').pack(fill=tk.X, padx=5, pady=5)

        # Text display area
        text_frame = ttk.Frame(self.root, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)

        self.text_display = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Arial", 12))
        self.text_display.pack(fill=tk.BOTH, expand=True)
        self.text_display.tag_configure("highlight", background="yellow", foreground="black")

    def browse_srt(self):
        file_path = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt"), ("All files", "*.*")])
        if file_path:
            self.srt_path_var.set(file_path)

            # Try to find matching audio file
            srt_dir = os.path.dirname(file_path)
            srt_name = os.path.splitext(os.path.basename(file_path))[0]

            for ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4']:
                potential_audio = os.path.join(srt_dir, srt_name + ext)
                if os.path.exists(potential_audio):
                    self.audio_path_var.set(potential_audio)
                    break

    def browse_audio(self):
        file_path = filedialog.askopenfilename(filetypes=[
            ("Audio files", "*.mp3 *.wav *.m4a *.flac *.ogg"),
            ("Video files", "*.mp4 *.mkv *.mov *.avi"),
            ("All files", "*.*")
        ])
        if file_path:
            self.audio_path_var.set(file_path)

    def parse_srt(self, srt_file):
        with open(srt_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract segments
        segments = re.findall(r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3}) --> (\d{2}:\d{2}:\d{2},\d{3})\n(.*?)(?=\n\n|\Z)',
                             content, re.DOTALL)

        words = []
        for _, start_time, end_time, text in segments:
            # Extract words with font tags
            word_matches = re.findall(r'<font color="#ff0000">(.*?)</font>', text)

            if word_matches:
                # Convert timestamp to seconds
                start_seconds = self.timestamp_to_seconds(start_time)
                end_seconds = self.timestamp_to_seconds(end_time)

                # Calculate approximate time for each word
                word_count = len(word_matches)
                duration = end_seconds - start_seconds
                word_duration = duration / word_count

                # Assign timestamps to each word
                for i, word in enumerate(word_matches):
                    word_start = start_seconds + (i * word_duration)
                    word_end = word_start + word_duration
                    words.append((word, word_start, word_end))

        return words

    def timestamp_to_seconds(self, timestamp):
        h, m, rest = timestamp.split(':')
        s, ms = rest.split(',')
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000

    def seconds_to_timestamp(self, seconds):
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"

    def load_files(self):
        srt_file = self.srt_path_var.get()
        audio_file = self.audio_path_var.get()

        if not srt_file or not os.path.exists(srt_file):
            messagebox.showerror("Error", "Please select a valid SRT file")
            return

        # If no audio file is specified or it doesn't exist, try to find it in the same folder
        if not audio_file or not os.path.exists(audio_file):
            srt_dir = os.path.dirname(srt_file)
            srt_name = os.path.splitext(os.path.basename(srt_file))[0]

            # Try common audio/video extensions
            for ext in ['.mp3', '.wav', '.m4a', '.flac', '.ogg', '.mp4', '.mkv', '.mov']:
                potential_audio = os.path.join(srt_dir, srt_name + ext)
                if os.path.exists(potential_audio):
                    audio_file = potential_audio
                    self.audio_path_var.set(audio_file)
                    break

            if not audio_file or not os.path.exists(audio_file):
                messagebox.showerror("Error", "Please select a valid audio file or place it in the same folder as the SRT file")
                return

        # Parse SRT file
        self.words = self.parse_srt(srt_file)

        if not self.words:
            messagebox.showwarning("Warning", "No word timestamps found in the SRT file. Make sure it contains word-level timestamps.")

        # Load audio file
        try:
            # Reinitialize pygame mixer to avoid issues
            pygame.mixer.quit()
            pygame.mixer.init()

            pygame.mixer.music.load(audio_file)
            self.audio_file = audio_file
            self.srt_file = srt_file

            # Display text
            self.display_text()

            # Update UI
            self.play_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.NORMAL)

            # Get audio duration - use a different approach
            try:
                sound = pygame.mixer.Sound(audio_file)
                self.audio_duration = sound.get_length()
            except:
                # If we can't get the length, use a default value
                self.audio_duration = 300  # 5 minutes default
                messagebox.showinfo("Info", "Could not determine audio duration. Using default value.")

            self.progress_bar.config(to=self.audio_duration)

            messagebox.showinfo("Success", f"Loaded SRT file with {len(self.words)} words and audio file successfully.")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load audio file: {str(e)}")

    def display_text(self):
        self.text_display.delete(1.0, tk.END)

        # Create a plain text version
        plain_text = " ".join([word[0] for word in self.words])
        self.text_display.insert(tk.END, plain_text)

        # Create word indices for highlighting
        self.word_indices = []
        current_index = "1.0"

        for word, _, _ in self.words:
            # Find the word in the text
            start_index = self.text_display.search(word, current_index, tk.END)
            if not start_index:
                continue

            end_index = f"{start_index}+{len(word)}c"
            self.word_indices.append((start_index, end_index))
            current_index = end_index

    def toggle_playback(self):
        if not self.audio_file or not os.path.exists(self.audio_file):
            messagebox.showerror("Error", "No audio file loaded. Please load an audio file first.")
            return

        try:
            if self.playing:
                pygame.mixer.music.pause()
                self.play_button.config(text="▶ Play Audio")
                self.playing = False
            else:
                if pygame.mixer.music.get_pos() == -1:  # Not started yet
                    # Make sure the audio file is loaded
                    try:
                        pygame.mixer.music.load(self.audio_file)
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to load audio file: {str(e)}")
                        return

                    pygame.mixer.music.play()
                    self.start_time = time.time()
                    self.current_time = 0
                else:
                    pygame.mixer.music.unpause()
                    self.start_time = time.time() - self.current_time

                self.play_button.config(text="⏸ Pause")
                self.playing = True

                # Start update thread
                threading.Thread(target=self.update_playback, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Playback Error", f"Error during playback: {str(e)}")

    def stop_playback(self):
        try:
            pygame.mixer.music.stop()
            self.play_button.config(text="▶ Play Audio")
            self.playing = False
            self.current_time = 0
            self.progress_var.set(0)
            self.time_var.set("00:00:00.000")

            # Remove all highlights
            self.text_display.tag_remove("highlight", "1.0", tk.END)
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping playback: {str(e)}")

    def seek(self, value):
        if not self.playing and hasattr(self, 'audio_duration'):
            position = float(value)
            self.current_time = position
            self.time_var.set(self.seconds_to_timestamp(position))

            # Update highlighted words
            self.highlight_current_words(position)

    def update_playback(self):
        while self.playing:
            if pygame.mixer.music.get_busy():
                self.current_time = time.time() - self.start_time
                self.progress_var.set(self.current_time)
                self.time_var.set(self.seconds_to_timestamp(self.current_time))

                # Update highlighted words
                self.highlight_current_words(self.current_time)

                time.sleep(0.05)
            else:
                self.stop_playback()
                break

    def highlight_current_words(self, current_time):
        # Remove all highlights
        self.text_display.tag_remove("highlight", "1.0", tk.END)

        # Find words that should be highlighted
        for i, (_, start_time, end_time) in enumerate(self.words):  # Use _ to ignore unused variable
            if start_time <= current_time <= end_time:
                if i < len(self.word_indices):
                    start_idx, end_idx = self.word_indices[i]
                    self.text_display.tag_add("highlight", start_idx, end_idx)

                    # Ensure the highlighted word is visible
                    self.text_display.see(start_idx)

if __name__ == "__main__":
    root = tk.Tk()
    app = SRTVisualizer(root)
    root.mainloop()
