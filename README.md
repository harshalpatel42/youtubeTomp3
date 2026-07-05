# YouTube Media Downloader

A lightweight, graphical desktop application that allows you to seamlessly download YouTube videos or extract high-quality MP3 audio. Built with Python, Tkinter, and powered by `yt-dlp`.

## Features
*   **Clean Graphical Interface:** No terminal commands required. Paste your link, choose your folder, and click download.
*   **Smart Video Quality:** Set a maximum video resolution (360p, 720p, 1080p, or Uncapped "Best"). The app automatically fetches the highest available quality below your ceiling.
*   **Audio Extraction:** Instantly strips video and converts the audio track to a high-quality 192kbps MP3.
*   **Auto-Updater:** The application automatically checks for new releases on launch and prompts you to update if a newer version is available.

---

## How to Use the App
1. Go to the [Releases](../../releases/latest) page on this repository.
2. Download the latest `.exe` file.
3. Run the application. 
4. Paste your YouTube URL, select a download folder, choose your format, and hit Download!

*(Note: The application runs a background process to check for updates when first opened. If Windows Defender flags it, this is simply because it is an unsigned indie executable checking the internet.)*

---

## Developer Instructions

If you want to clone this repository, modify the code, and compile your own custom executable, follow these steps.

### Prerequisites
1. **Python 3.x** installed on your system.
2. **Poetry** installed for dependency management.
3. **FFmpeg** installed and added to your system's system PATH (required by `yt-dlp` for converting files to MP4 and MP3).

### Installation
Clone the repository and install the required dependencies using Poetry:
```bash
git clone [https://github.com/harshalpatel42/youtubeTomp3.git](https://github.com/harshalpatel42/youtubeTomp3.git)
cd youtubeTomp3
poetry install


poetry run pyinstaller --onefile --noconsole --name "YouTube Media Downloader" youtube.py