import os
import sys
import time
import requests
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import yt_dlp

CURRENT_VERSION = 1.0
VERSION_URL = "https://raw.githubusercontent.com/harshalpatel42/youtubeTomp3/master/version.txt"
DOWNLOAD_URL = "https://github.com/harshalpatel42/youtubeTomp3/releases/latest/download/youtube.exe"

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

    status_var.set("Downloading... Please wait.")
    download_btn.config(state=tk.DISABLED)

    ydl_opts = {
        'outtmpl': os.path.join(folder, '%(title)s.%(ext)s'),
        'restrictfilenames': True,
        'windowsfilenames': True,
        'quiet': True,
        'no_warnings': True,
    }

    if format_choice == 'V':
        if quality == "Best":
            ydl_opts['format'] = 'bestvideo+bestaudio/best'
        else:
            res_number = quality.replace('p', '')
            ydl_opts['format'] = f'bestvideo[height<={res_number}]+bestaudio/best'
            
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',
        }]
    else:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(url, download=True)
        status_var.set("Success! Download complete.")
    except Exception:
        status_var.set("Error: Download failed. Check URL or FFmpeg.")
    finally:
        download_btn.config(state=tk.NORMAL)

def start_download_thread():
    threading.Thread(target=execute_download, daemon=True).start()

root = tk.Tk()
root.title("YouTube Media Downloader")
root.geometry("500x350")
root.resizable(False, False)

url_var = tk.StringVar()
folder_var = tk.StringVar()
format_var = tk.StringVar(value="A")
quality_var = tk.StringVar(value="720p")
status_var = tk.StringVar(value="Ready")

format_var.trace_add("write", toggle_quality_menu)

frame = tk.Frame(root, padx=20, pady=20)
frame.pack(fill=tk.BOTH, expand=True)

tk.Label(frame, text="Video URL:").pack(anchor="w")
tk.Entry(frame, textvariable=url_var, width=50).pack(fill=tk.X, pady=(0, 15))

tk.Label(frame, text="Save Location:").pack(anchor="w")
folder_frame = tk.Frame(frame)
folder_frame.pack(fill=tk.X, pady=(0, 15))
tk.Entry(folder_frame, textvariable=folder_var, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)
tk.Button(folder_frame, text="Browse", command=browse_folder).pack(side=tk.RIGHT, padx=(5, 0))

options_frame = tk.Frame(frame)
options_frame.pack(fill=tk.X, pady=(0, 20))

tk.Label(options_frame, text="Format:").pack(side=tk.LEFT)
tk.Radiobutton(options_frame, text="Audio (MP3)", variable=format_var, value="A").pack(side=tk.LEFT, padx=10)
tk.Radiobutton(options_frame, text="Video (MP4)", variable=format_var, value="V").pack(side=tk.LEFT)

tk.Label(options_frame, text="Max Video Quality:").pack(side=tk.LEFT, padx=(20, 5))
quality_dropdown = ttk.Combobox(options_frame, textvariable=quality_var, values=["360p", "720p", "1080p", "Best"], width=8, state="disabled")
quality_dropdown.pack(side=tk.LEFT)

download_btn = tk.Button(frame, text="Download", command=start_download_thread, bg="#4CAF50", fg="white", font=("Arial", 12, "bold"), pady=5)
download_btn.pack(fill=tk.X, pady=(10, 20))

tk.Label(frame, textvariable=status_var, fg="gray", font=("Arial", 9, "italic")).pack()

threading.Thread(target=check_for_updates, daemon=True).start()

root.mainloop()