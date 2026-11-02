import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp

class VideoDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Downloader - yt-dlp")
        self.root.geometry("600x450")
        self.root.resizable(False, False)
        
        # Get ffmpeg path
        self.ffmpeg_path = self.get_ffmpeg_path()
        
        self.create_widgets()
        
    def get_ffmpeg_path(self):
        # Check if running from PyInstaller bundle
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        # Check in bundled folder
        ffmpeg_path = os.path.join(base_path, "ffmpeg", "bin", "ffmpeg.exe")
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path
        
        # Check in current directory
        ffmpeg_path = os.path.join(os.getcwd(), "ffmpeg", "bin", "ffmpeg.exe")
        if os.path.exists(ffmpeg_path):
            return ffmpeg_path
        
        # Check if ffmpeg is in PATH
        try:
            subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
            return "ffmpeg"
        except:
            return None
    
    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="Video Downloader", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # URL Input
        url_frame = tk.Frame(self.root)
        url_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(url_frame, text="URL:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.url_entry = tk.Entry(url_frame, font=("Arial", 10), width=50)
        self.url_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        # Quality Selection
        quality_frame = tk.LabelFrame(self.root, text="Quality / Format", font=("Arial", 10, "bold"))
        quality_frame.pack(pady=10, padx=20, fill=tk.X)
        
        self.quality_var = tk.StringVar(value="best")
        
        qualities = [
            ("MP4 - Best Quality (1080p+)", "best"),
            ("MP4 - Medium Quality (720p)", "720"),
            ("MP4 - Low Quality (480p)", "480"),
            ("MP3 - Audio Only", "audio")
        ]
        
        for text, value in qualities:
            rb = tk.Radiobutton(quality_frame, text=text, variable=self.quality_var, 
                              value=value, font=("Arial", 9))
            rb.pack(anchor=tk.W, padx=10, pady=2)
        
        # Download Location
        location_frame = tk.Frame(self.root)
        location_frame.pack(pady=10, padx=20, fill=tk.X)
        
        tk.Label(location_frame, text="Save to:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.location_entry = tk.Entry(location_frame, font=("Arial", 10), width=40)
        self.location_entry.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.location_entry.insert(0, os.path.join(os.path.expanduser("~"), "Downloads"))
        
        browse_btn = tk.Button(location_frame, text="Browse", command=self.browse_location, 
                              font=("Arial", 9), width=8)
        browse_btn.pack(side=tk.LEFT)
        
        # Download Button
        self.download_btn = tk.Button(self.root, text="Download", command=self.start_download,
                                     font=("Arial", 11, "bold"), bg="#4CAF50", fg="white",
                                     height=2, width=20)
        self.download_btn.pack(pady=15)
        
        # Progress Bar
        self.progress = ttk.Progressbar(self.root, mode='determinate', length=500)
        self.progress.pack(pady=5)
        
        # Status Label
        self.status_label = tk.Label(self.root, text="Ready", font=("Arial", 9), fg="gray")
        self.status_label.pack(pady=5)
        
        # Check ffmpeg
        if not self.ffmpeg_path:
            self.status_label.config(text="Warning: FFmpeg not found!", fg="red")
    
    def browse_location(self):
        folder = filedialog.askdirectory()
        if folder:
            self.location_entry.delete(0, tk.END)
            self.location_entry.insert(0, folder)
    
    def start_download(self):
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a URL")
            return
        
        save_path = self.location_entry.get().strip()
        if not os.path.exists(save_path):
            messagebox.showerror("Error", "Invalid save location")
            return
        
        self.download_btn.config(state=tk.DISABLED, text="Downloading...")
        self.status_label.config(text="Starting download...", fg="blue")
        
        # Start download in separate thread
        thread = threading.Thread(target=self.download_video, args=(url, save_path))
        thread.daemon = True
        thread.start()
    
    def download_video(self, url, save_path):
        try:
            quality = self.quality_var.get()
            
            # Configure yt-dlp options
            ydl_opts = {
                'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
                'progress_hooks': [self.progress_hook],
            }
            
            if self.ffmpeg_path:
                ydl_opts['ffmpeg_location'] = self.ffmpeg_path
            
            if quality == "audio":
                ydl_opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
            elif quality == "best":
                ydl_opts.update({
                    'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                    'merge_output_format': 'mp4',
                })
            elif quality == "720":
                ydl_opts.update({
                    'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best[height<=720]',
                    'merge_output_format': 'mp4',
                })
            elif quality == "480":
                ydl_opts.update({
                    'format': 'bestvideo[height<=480][ext=mp4]+bestaudio[ext=m4a]/best[height<=480][ext=mp4]/best[height<=480]',
                    'merge_output_format': 'mp4',
                })
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            self.root.after(0, self.download_complete, True, "Download completed successfully!")
            
        except Exception as e:
            self.root.after(0, self.download_complete, False, str(e))
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', '0%').replace('%', '')
                self.root.after(0, self.update_progress, float(percent))
                self.root.after(0, self.update_status, 
                    f"Downloading: {d.get('_speed_str', '')} - {d.get('_eta_str', '')}", "blue")
            except:
                pass
        elif d['status'] == 'finished':
            self.root.after(0, self.update_progress, 100)
            self.root.after(0, self.update_status, "Processing...", "orange")
    
    def update_progress(self, value):
        self.progress['value'] = value
    
    def update_status(self, text, color):
        self.status_label.config(text=text, fg=color)
    
    def download_complete(self, success, message):
        self.download_btn.config(state=tk.NORMAL, text="Download")
        self.progress['value'] = 0
        
        if success:
            self.status_label.config(text=message, fg="green")
            messagebox.showinfo("Success", message)
        else:
            self.status_label.config(text=f"Error: {message}", fg="red")
            messagebox.showerror("Error", message)

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoDownloader(root)
    root.mainloop()
