from datetime import datetime
from pathlib import Path

import pyautogui


BASE_DIR = Path(__file__).resolve().parent.parent
SCREENSHOT_DIR = BASE_DIR / "screenshots"


def screenshot():
    SCREENSHOT_DIR.mkdir(exist_ok=True)

    filename = datetime.now().strftime(
        "screenshot_%Y%m%d_%H%M%S.png"
    )

    path = SCREENSHOT_DIR / filename

    image = pyautogui.screenshot()

    image.save(path)

    return True, f"Screenshot saved as {filename}."