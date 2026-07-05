import os
import sys
import re
import requests
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import yt_dlp

CURRENT_VERSION = 1.1
VERSION_URL = "https://raw.githubusercontent.com/harshalpatel42/youtubeTomp3/master/version.txt"
DOWNLOAD_URL = "https://github.com/harshalpatel42/youtubeTomp3/releases/download/latest/ytdownloader.exe"

# Global flag to handle cancellations safely across threads
cancel_event = threading.Event()

def check_for_updates():
    try:
        response = requests.get(VERSION_URL, timeout=5)
        latest_version = float(response.text.strip())
        
        if latest_version > CURRENT_VERSION:
            prompt = messagebox.askyesno(
                "Update Available", 
                f"Version {latest_version} is available! You are on v{CURRENT_VERSION}.\n\nWould you like to update now?"
            )
            if prompt:
                download_and_apply_update()
    except Exception:
        pass

def download_and_apply_update():
    try:
        new_exe_name = "update_temp.exe"
        response = requests.get(DOWNLOAD_URL, stream=True)
        
        with open(new_exe_name, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
                
        current_exe_name = os.path.basename(sys.executable)
        
        bat_script = f"""@echo off
timeout /t 2 /nobreak > NUL
del "{current_exe_name}"
ren "{new_exe_name}" "{current_exe_name}"
start "" "{current_exe_name}"
del "%~f0"
"""
        with open("updater.bat", "w") as bat_file:
            bat_file.write(bat_script)
            
        subprocess.Popen("updater.bat", shell=True)
        sys.exit()
        
    except Exception as e:
        messagebox.showerror("Update Failed", f"Could not apply update: {e}")

def browse_folder():
    folder_path = filedialog.askdirectory(title="Select Folder to Save Media")
    if folder_path:
        folder_var.set(folder_path)

def toggle_quality_menu(*args):
    if format_var.get() == 'V':
        quality_dropdown.config(state='readonly')
    else:
        quality_dropdown.config(state='disabled')

def cancel_download():
    cancel_event.set()
    status_var.set("Cancelling... Please wait.")
    cancel_btn.config(state=tk.DISABLED)

def progress_hook(d):
    if cancel_event.is_set():
        raise Exception("Download Cancelled by User")
    
    if d['status'] == 'downloading':
        try:
            # Clean yt-dlp's percent string of ANSI escape codes
            p_str = d.get('_percent_str', '0.0%').replace('%', '').strip()
            p_clean = re.sub(r'\x1b\[[0-9;]*m', '', p_str)
            progress_var.set(float(p_clean))
            root.update_idletasks()
        except Exception:
            pass

def execute_download():
    url = url_var.get().strip()
    folder = folder_var.get().strip()
    format_choice = format_var.get()
    quality = quality_var.get()

    if not url:
        status_var.set("Error: URL cannot be empty!")
        return
    if not folder:
        status_var.set("Error: Please select a save folder.")
        return

    cancel_event.clear()
    progress_var.set(0)
    status_var.set("Downloading... Please wait.")
    download_btn.config(state=tk.DISABLED)
    cancel_btn.config(state=tk.NORMAL)

    ydl_opts = {
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'windowsfilenames': True,
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [progress_hook],
        'noplaylist': not playlist_var.get(),
        'writethumbnail': True,
    }

    ydl_opts['postprocessors'] = []

    if format_choice == 'V':
        if quality == "Best":
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            res_number = quality.replace('p', '')
            ydl_opts['format'] = f'bestvideo[height<={res_number}]+bestaudio/best'
            
        ydl_opts['postprocessors'].extend([
            {'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'},
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'},
        ])
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'].extend([
            {'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'},
            {'key': 'FFmpegMetadata'},
            {'key': 'EmbedThumbnail'},
        ])

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
            
        if not cancel_event.is_set():
            status_var.set("Success! Download complete.")
            progress_var.set(100.0)
    except Exception as e:
        if cancel_event.is_set():
            status_var.set("Download successfully cancelled.")
            progress_var.set(0)
        else:
            status_var.set("Error: Download failed. Check URL or FFmpeg.")
    finally:
        download_btn.config(state=tk.NORMAL)
        cancel_btn.config(state=tk.DISABLED)

def start_download_thread():
    threading.Thread(target=execute_download, daemon=True).start()

root = tk.Tk()
root.title("YouTube Media Downloader v1.1")
root.geometry("500x420")
root.resizable(False, False)

url_var = tk.StringVar()
folder_var = tk.StringVar()
format_var = tk.StringVar(value="A")
quality_var = tk.StringVar(value="720p")
status_var = tk.StringVar(value="Ready")
playlist_var = tk.BooleanVar(value=False)
progress_var = tk.DoubleVar(value=0.0)

format_var.trace_add("write", toggle_quality_menu)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(fill=tk.BOTH, expand=True)

tk.Label(frame, text="Video or Playlist URL:").pack(anchor="w")
tk.Entry(frame, textvariable=url_var, width=50).pack(fill=tk.X, pady=(0, 15))

tk.Label(frame, text="Save Location:").pack(anchor="w")
folder_frame = tk.Frame(frame)
folder_frame.pack(fill=tk.X, pady=(0, 15))
tk.Entry(folder_frame, textvariable=folder_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(folder_frame, text="Browse", command=browse_folder).pack(side=tk.RIGHT, padx=(5, 0))

options_frame = tk.Frame(frame)
options_frame.pack(fill=tk.X, pady=(0, 10))

tk.Label(options_frame, text="Format:").pack(side=tk.LEFT)
tk.Radiobutton(options_frame, text="Audio", variable=format_var, value="A").pack(side=tk.LEFT, padx=5)
tk.Radiobutton(options_frame, text="Video", variable=format_var, value="V").pack(side=tk.LEFT)

tk.Label(options_frame, text="Quality:").pack(side=tk.LEFT, padx=(15, 5))
quality_dropdown = ttk.Combobox(options_frame, textvariable=quality_var, values=["360p", "720p", "1080p", "Best"], width=6, state="disabled")
quality_dropdown.pack(side=tk.LEFT)

tk.Checkbutton(options_frame, text="Download Entire Playlist", variable=playlist_var).pack(side=tk.RIGHT)

button_frame = tk.Frame(frame)
button_frame.pack(fill=tk.X, pady=(10, 10))

download_btn = tk.Button(button_frame, text="Download", command=start_download_thread, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), width=18)
download_btn.pack(side=tk.LEFT, expand=True, padx=(0, 5))

cancel_btn = tk.Button(button_frame, text="Cancel", command=cancel_download, state=tk.DISABLED, bg="#F44336", fg="white", font=("Arial", 11, "bold"), width=18)
cancel_btn.pack(side=tk.RIGHT, expand=True, padx=(5, 0))

progress_bar = ttk.Progressbar(frame, variable=progress_var, maximum=100)
progress_bar.pack(fill=tk.X, pady=(10, 5))

tk.Label(frame, textvariable=status_var, fg="gray", font=("Arial", 9, "italic")).pack()

threading.Thread(target=check_for_updates, daemon=True).start()

root.mainloop()