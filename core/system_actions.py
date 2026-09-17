"""
SARATHI system actions.

All the "do something on this PC" logic lives here, kept separate from
assistant.py so the command logic and the conversational logic don't
tangle together. Written for Windows (matches notepad.exe / calc.exe
usage elsewhere in the project).
"""

import ctypes
import os
import shutil
import subprocess
import webbrowser
from datetime import datetime
from pathlib import Path
from urllib.parse import quote_plus

HOME = Path.home()
NOTES_DIR = Path(__file__).resolve().parent.parent / "notes"
NOTES_DIR.mkdir(exist_ok=True)

FOLDER_PATHS = {
    "documents": HOME / "Documents",
    "downloads": HOME / "Downloads",
    "desktop": HOME / "Desktop",
    "pictures": HOME / "Pictures",
    "music": HOME / "Music",
    "videos": HOME / "Videos",
}

FOLDER_TALK = {
    "documents": "This is where most of your files and important documents live.",
    "downloads": "Everything you download from the internet usually ends up right here.",
    "desktop": "Your desktop, the first thing you see when you log in.",
    "pictures": "All your photos and images, in one place.",
    "music": "Your music library lives here.",
    "videos": "All your saved videos are kept in this folder.",
}


# ---------------------------------------------------------------------------
# Browsing & search
# ---------------------------------------------------------------------------
def open_browser():
    webbrowser.open("https://www.google.com")
    return "Opening your browser."


def search_google(query):
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(query)}")
    return f"Searching Google for {query}."


def search_youtube(query):
    webbrowser.open(f"https://www.youtube.com/results?search_query={quote_plus(query)}")
    return f"Searching YouTube for {query}."


def play_youtube_video(query):
    """Find the top YouTube result for query and open it playing directly."""
    import re
    import requests

    try:
        search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
        response = requests.get(
            search_url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
        if not video_ids:
            return f"I could not find a video for {query}."

        video_id = video_ids[0]
        webbrowser.open(f"https://www.youtube.com/watch?v={video_id}")
        return f"Playing {query} on YouTube."
    except Exception:
        return "I was not able to play that video right now. Please check your internet connection."


# ---------------------------------------------------------------------------
# Folders
# ---------------------------------------------------------------------------
def open_folder(name):
    name = name.strip().lower()

    if name in ("this pc", "my computer", "computer"):
        subprocess.Popen(["explorer.exe", "shell:MyComputerFolder"])
        return "Opening This PC. All your drives and storage, right here."

    path = FOLDER_PATHS.get(name)
    if path is None:
        return f"I do not know a folder called {name}."

    if not path.exists():
        return f"I could not find your {name} folder."

    subprocess.Popen(["explorer.exe", str(path)])
    talk = FOLDER_TALK.get(name, "")
    return f"Opening your {name} folder. {talk}".strip()


# ---------------------------------------------------------------------------
# Writing / notes
# ---------------------------------------------------------------------------
def write_note(text):
    """Save dictated text to a timestamped .txt file and open it."""
    text = text.strip()
    if not text:
        return "I did not catch anything to write down."

    filename = datetime.now().strftime("note_%Y-%m-%d_%H-%M-%S.txt")
    filepath = NOTES_DIR / filename

    filepath.write_text(text, encoding="utf-8")
    subprocess.Popen(["notepad.exe", str(filepath)])
    return "I have written that down and opened it for you."


# ---------------------------------------------------------------------------
# Troubleshooting / "find problems and solve them"
# ---------------------------------------------------------------------------
def check_internet():
    try:
        result = subprocess.run(
            ["ping", "-n", "2", "8.8.8.8"],
            capture_output=True,
            timeout=10,
        )
        if result.returncode == 0:
            return "Your internet connection looks fine."
        return "I am not able to reach the internet right now. Your connection may be down."
    except Exception:
        return "I was not able to test your internet connection."


def check_disk_space(drive="C:\\"):
    try:
        total, used, free = shutil.disk_usage(drive)
        free_gb = free // (2**30)
        total_gb = total // (2**30)
        percent_free = round((free / total) * 100)

        if percent_free < 10:
            warning = " That is quite low, you may want to free up some space."
        else:
            warning = ""

        return (
            f"You have {free_gb} gigabytes free out of {total_gb} gigabytes on drive {drive.strip(chr(92))}."
            f"{warning}"
        )
    except Exception:
        return "I was not able to check your disk space."


def flush_dns():
    try:
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, timeout=10)
        return "I have flushed your DNS cache. That can help fix some connection issues."
    except Exception:
        return "I was not able to flush the DNS cache."


def clear_temp_files():
    temp_dir = Path(os.environ.get("TEMP", ""))
    if not temp_dir.exists():
        return "I could not find your temporary files folder."

    cleared = 0
    skipped = 0
    for item in temp_dir.iterdir():
        try:
            if item.is_file():
                item.unlink()
            else:
                shutil.rmtree(item, ignore_errors=True)
            cleared += 1
        except Exception:
            skipped += 1

    return f"I cleared {cleared} temporary items. {skipped} were in use and left alone."


def empty_recycle_bin():
    try:
        # SHEmptyRecycleBinW flags: 0x1 no confirm, 0x2 no progress, 0x4 no sound
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 0x1 | 0x2 | 0x4)
        return "I have emptied the Recycle Bin."
    except Exception:
        return "I was not able to empty the Recycle Bin. It may already be empty."


def run_quick_checkup():
    """A one-shot 'find problems' report covering the common stuff."""
    lines = [
        check_internet(),
        check_disk_space(),
    ]
    return " ".join(lines)


# ---------------------------------------------------------------------------
# More apps
# ---------------------------------------------------------------------------
APP_COMMANDS = {
    "word": ["winword.exe"],
    "excel": ["excel.exe"],
    "powerpoint": ["powerpnt.exe"],
    "paint": ["mspaint.exe"],
    "task manager": ["taskmgr.exe"],
    "control panel": ["control.exe"],
    "settings": ["start", "ms-settings:"],
    "command prompt": ["cmd.exe"],
    "snipping tool": ["snippingtool.exe"],
}

APP_TALK = {
    "word": "Great for writing letters, reports, or anything that needs proper formatting.",
    "excel": "Perfect for spreadsheets, budgets, and anything involving numbers.",
    "powerpoint": "Time to put together some slides.",
    "paint": "Simple and classic, good for quick sketches or edits.",
    "task manager": "Here you can see everything running on your computer right now.",
    "control panel": "This is where you can manage most of your system settings.",
    "settings": "All your system preferences live here.",
    "command prompt": "The command line, for when you want to talk to your computer directly.",
    "snipping tool": "Perfect for grabbing a quick screenshot of anything on screen.",
    "notepad": "Simple, fast, and great for jotting things down without any clutter.",
    "calculator": "Quick maths, right at your fingertips.",
}

# Process names used to close apps. Some apps have multiple possible
# process names depending on Windows version.
CLOSE_PROCESS_NAMES = {
    "word": ["winword.exe"],
    "excel": ["excel.exe"],
    "powerpoint": ["powerpnt.exe"],
    "paint": ["mspaint.exe"],
    "task manager": ["taskmgr.exe"],
    "control panel": ["control.exe"],
    "settings": ["systemsettings.exe"],
    "command prompt": ["cmd.exe"],
    "snipping tool": ["snippingtool.exe", "screenclippinghost.exe"],
    "notepad": ["notepad.exe"],
    "calculator": ["calculatorapp.exe", "calc.exe"],
    "browser": ["chrome.exe", "msedge.exe", "firefox.exe"],
    "chrome": ["chrome.exe"],
    "edge": ["msedge.exe"],
    "youtube": ["chrome.exe", "msedge.exe", "firefox.exe"],
    "google": ["chrome.exe", "msedge.exe", "firefox.exe"],
}


def open_app(name):
    name = name.strip().lower()
    command = APP_COMMANDS.get(name)
    if command is None:
        return f"I do not know how to open {name} yet."

    try:
        if command[0] == "start":
            subprocess.Popen(command, shell=True)
        else:
            subprocess.Popen(command)
        talk = APP_TALK.get(name, "")
        return f"Opening {name} for you. {talk}".strip()
    except FileNotFoundError:
        return f"I could not find {name} installed on this computer."


def close_app(name):
    name = name.strip().lower()
    processes = CLOSE_PROCESS_NAMES.get(name)
    if processes is None:
        return f"I do not know how to close {name}."

    closed_any = False
    for process_name in processes:
        result = subprocess.run(
            ["taskkill", "/F", "/IM", process_name],
            capture_output=True,
        )
        if result.returncode == 0:
            closed_any = True

    if closed_any:
        if name in ("youtube", "google"):
            return f"That is a browser tab, so I closed your whole browser to close {name}."
        return f"Closed {name} for you."
    return f"I could not find {name} running."


# ---------------------------------------------------------------------------
# Power / lock
# ---------------------------------------------------------------------------
def lock_pc():
    ctypes.windll.user32.LockWorkStation()
    return "Locking your computer now."


def shutdown_pc(delay_seconds=60):
    subprocess.run(["shutdown", "/s", "/t", str(delay_seconds)])
    return f"Shutting down in {delay_seconds} seconds. Say cancel shutdown if you change your mind."


def restart_pc(delay_seconds=60):
    subprocess.run(["shutdown", "/r", "/t", str(delay_seconds)])
    return f"Restarting in {delay_seconds} seconds. Say cancel shutdown if you change your mind."


def cancel_shutdown():
    subprocess.run(["shutdown", "/a"])
    return "Shutdown cancelled."


# ---------------------------------------------------------------------------
# Screenshot
# ---------------------------------------------------------------------------
def take_screenshot():
    try:
        from PIL import ImageGrab
    except ImportError:
        return "I need the Pillow library for screenshots. Please run pip install pillow."

    filename = datetime.now().strftime("screenshot_%Y-%m-%d_%H-%M-%S.png")
    filepath = NOTES_DIR / filename
    image = ImageGrab.grab()
    image.save(filepath)
    subprocess.Popen(["explorer.exe", "/select,", str(filepath)])
    return "I have taken a screenshot and saved it for you."


# ---------------------------------------------------------------------------
# Fun / games
# ---------------------------------------------------------------------------
def flip_coin():
    import random
    return f"It is {random.choice(['heads', 'tails'])}."


def roll_dice(sides=6):
    import random
    return f"You rolled a {random.randint(1, sides)}."