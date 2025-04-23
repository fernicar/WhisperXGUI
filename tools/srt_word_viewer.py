import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext, messagebox
import re
import os
import time
from pathlib import Path

class SRTWordViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("SRT Word Timestamp Viewer")
        self.root.geometry("800x600")
        
        # Variables
        self.srt_file = None
        self.words = []  # List of (word, start_time, end_time) tuples
        self.current_word_index = 0
        self.timer_running = False
        self.timer_id = None
        
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
        
        # Load button
        ttk.Button(file_frame, text="Load SRT", command=self.load_srt).grid(row=1, column=1, padx=5, pady=10)
        
        # Text display area
        text_frame = ttk.Frame(self.root, padding="10")
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.text_display = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, font=("Arial", 12))
        self.text_display.pack(fill=tk.BOTH, expand=True)
        self.text_display.tag_configure("highlight", background="yellow", foreground="black")
        
        # Playback simulation controls
        control_frame = ttk.Frame(self.root, padding="10")
        control_frame.pack(fill=tk.X)
        
        self.start_button = ttk.Button(control_frame, text="Start Simulation", command=self.start_simulation)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Stop Simulation", command=self.stop_simulation)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.config(state=tk.DISABLED)
        
        # Speed control
        ttk.Label(control_frame, text="Speed:").pack(side=tk.LEFT, padx=(20, 5))
        self.speed_var = tk.DoubleVar(value=1.0)
        speed_options = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        self.speed_combo = ttk.Combobox(control_frame, textvariable=self.speed_var, values=speed_options, width=5)
        self.speed_combo.pack(side=tk.LEFT, padx=5)
        self.speed_combo.current(2)  # Default to 1.0
        
        # Time display
        self.time_var = tk.StringVar(value="00:00:00.000")
        ttk.Label(control_frame, textvariable=self.time_var).pack(side=tk.RIGHT, padx=5)
        
        # Word navigation
        word_frame = ttk.Frame(self.root, padding="10")
        word_frame.pack(fill=tk.X)
        
        ttk.Button(word_frame, text="Previous Word", command=lambda: self.navigate_words(-1)).pack(side=tk.LEFT, padx=5)
        ttk.Button(word_frame, text="Next Word", command=lambda: self.navigate_words(1)).pack(side=tk.LEFT, padx=5)
        
        self.current_word_var = tk.StringVar(value="No word selected")
        ttk.Label(word_frame, textvariable=self.current_word_var).pack(side=tk.LEFT, padx=20)
    
    def browse_srt(self):
        file_path = filedialog.askopenfilename(filetypes=[("SRT files", "*.srt"), ("All files", "*.*")])
        if file_path:
            self.srt_path_var.set(file_path)
    
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
    
    def load_srt(self):
        srt_file = self.srt_path_var.get()
        
        if not srt_file or not os.path.exists(srt_file):
            messagebox.showerror("Error", "Please select a valid SRT file")
            return
        
        # Parse SRT file
        self.words = self.parse_srt(srt_file)
        
        if not self.words:
            messagebox.showwarning("Warning", "No word timestamps found in the SRT file. Make sure it contains word-level timestamps.")
            return
        
        self.srt_file = srt_file
        
        # Display text
        self.display_text()
        
        # Enable controls
        self.start_button.config(state=tk.NORMAL)
        
        messagebox.showinfo("Success", f"Loaded SRT file with {len(self.words)} words successfully.")
        
        # Set current word to first word
        self.current_word_index = 0
        self.highlight_word(self.current_word_index)
    
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
    
    def start_simulation(self):
        """Start simulating playback by highlighting words based on their timestamps"""
        if not self.words:
            messagebox.showerror("Error", "No SRT file loaded")
            return
        
        self.timer_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        # Start from the beginning
        self.current_word_index = 0
        self.highlight_word(self.current_word_index)
        
        # Start the timer
        self.start_time = time.time()
        self.update_simulation()
    
    def stop_simulation(self):
        """Stop the simulation"""
        self.timer_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        # Cancel any pending timer
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None
    
    def update_simulation(self):
        """Update the simulation by highlighting the current word based on elapsed time"""
        if not self.timer_running:
            return
        
        # Calculate elapsed time
        elapsed_time = (time.time() - self.start_time) * self.speed_var.get()
        self.time_var.set(self.seconds_to_timestamp(elapsed_time))
        
        # Find the current word based on elapsed time
        current_index = self.current_word_index
        found = False
        
        for i, (_, start_time, end_time) in enumerate(self.words):
            if start_time <= elapsed_time <= end_time:
                current_index = i
                found = True
                break
            elif start_time > elapsed_time:
                # We've gone past the current time, use the previous word
                if i > 0:
                    current_index = i - 1
                found = True
                break
        
        # If we didn't find a word and we're past the last word's end time, stop the simulation
        if not found and elapsed_time > self.words[-1][2]:
            self.stop_simulation()
            messagebox.showinfo("Simulation Complete", "Reached the end of the transcript.")
            return
        
        # Update the highlighted word if it changed
        if current_index != self.current_word_index:
            self.current_word_index = current_index
            self.highlight_word(self.current_word_index)
        
        # Schedule the next update
        self.timer_id = self.root.after(50, self.update_simulation)
    
    def navigate_words(self, direction):
        """Navigate to the previous or next word"""
        if not hasattr(self, 'current_word_index') or not self.words:
            return
        
        new_index = self.current_word_index + direction
        if 0 <= new_index < len(self.words):
            self.current_word_index = new_index
            self.highlight_word(self.current_word_index)
    
    def highlight_word(self, index):
        """Highlight a specific word by index"""
        if not self.words or index >= len(self.words):
            return
        
        # Remove all highlights
        self.text_display.tag_remove("highlight", "1.0", tk.END)
        
        # Highlight the specified word
        if index < len(self.word_indices):
            start_idx, end_idx = self.word_indices[index]
            self.text_display.tag_add("highlight", start_idx, end_idx)
            
            # Ensure the highlighted word is visible
            self.text_display.see(start_idx)
            
            # Update current word display
            word, start_time, end_time = self.words[index]
            self.current_word_var.set(f"Word: '{word}' ({start_time:.2f}s - {end_time:.2f}s)")

if __name__ == "__main__":
    root = tk.Tk()
    app = SRTWordViewer(root)
    root.mainloop()
