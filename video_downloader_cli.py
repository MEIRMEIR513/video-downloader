import os
import sys
import subprocess
import yt_dlp

class VideoDownloaderCLI:
    def __init__(self):
        self.ffmpeg_path = self.get_ffmpeg_path()
    
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
    
    def download(self, url, quality, save_path):
        try:
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
            
            print("\n✓ Download completed successfully!")
            
        except Exception as e:
            print(f"\n✗ Error: {e}")
    
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            try:
                percent = d.get('_percent_str', '0%')
                speed = d.get('_speed_str', '')
                eta = d.get('_eta_str', '')
                print(f"\rProgress: {percent} | Speed: {speed} | ETA: {eta}", end='', flush=True)
            except:
                pass
        elif d['status'] == 'finished':
            print("\nProcessing...")

def main():
    print("=" * 60)
    print("  Video Downloader - yt-dlp CLI")
    print("=" * 60)
    
    downloader = VideoDownloaderCLI()
    
    if not downloader.ffmpeg_path:
        print("⚠ Warning: FFmpeg not found! Some features may not work.")
    
    # Get URL
    url = input("\nEnter video URL: ").strip()
    if not url:
        print("Error: URL is required")
        return
    
    # Get quality
    print("\nSelect quality/format:")
    print("1. MP4 - Best Quality (1080p+)")
    print("2. MP4 - Medium Quality (720p)")
    print("3. MP4 - Low Quality (480p)")
    print("4. MP3 - Audio Only")
    
    choice = input("\nEnter choice (1-4): ").strip()
    quality_map = {
        "1": "best",
        "2": "720",
        "3": "480",
        "4": "audio"
    }
    quality = quality_map.get(choice, "best")
    
    # Get save path
    default_path = os.path.join(os.path.expanduser("~"), "Downloads")
    save_path = input(f"\nSave to (default: {default_path}): ").strip()
    if not save_path:
        save_path = default_path
    
    if not os.path.exists(save_path):
        print(f"Error: Path does not exist: {save_path}")
        return
    
    # Download
    print(f"\nDownloading to: {save_path}")
    downloader.download(url, quality, save_path)

if __name__ == "__main__":
    main()
