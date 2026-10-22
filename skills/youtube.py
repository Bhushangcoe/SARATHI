import time

from core.browser_manager import browser


YOUTUBE_URL = "https://www.youtube.com"


def open_youtube():
    page = browser.open(YOUTUBE_URL)

    return True, "YouTube is open."


def search_youtube(query: str):
    page = browser.start()

    url = f"https://www.youtube.com/results?search_query={query.replace(' ', '+')}"

    page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=30000
    )

    time.sleep(2)

    return True, f"I searched YouTube for {query}."


def play_first_video():
    page = browser.start()

    try:
        video = page.locator("ytd-video-renderer a#video-title").first

        video.click(timeout=10000)

        time.sleep(2)

        return True, "Playing the first video."

    except Exception as exc:
        print(f"YouTube play error: {exc}")
        return False, "I couldn't find the first video."


def _keyboard(key: str):
    page = browser.start()

    page.keyboard.press(key)

    return True


def pause():
    return _keyboard("k"), "Video paused."


def resume():
    return _keyboard("k"), "Video resumed."


def next_video():
    page = browser.start()

    page.keyboard.press("SHIFT+N")

    return True, "Moving to the next video."


def previous_video():
    page = browser.start()

    page.keyboard.press("SHIFT+P")

    return True, "Going to the previous video."


def skip_forward(seconds=10):
    page = browser.start()

    try:
        seconds = int(seconds)
    except Exception:
        seconds = 10

    presses = max(1, round(seconds / 5))

    for _ in range(presses):
        page.keyboard.press("ARROWRIGHT")

    return True, f"Skipped forward about {seconds} seconds."


def skip_backward(seconds=10):
    page = browser.start()

    try:
        seconds = int(seconds)
    except Exception:
        seconds = 10

    presses = max(1, round(seconds / 5))

    for _ in range(presses):
        page.keyboard.press("ARROWLEFT")

    return True, f"Went back about {seconds} seconds."


def mute():
    page = browser.start()

    page.keyboard.press("m")

    return True, "Video muted."


def unmute():
    page = browser.start()

    page.keyboard.press("m")

    return True, "Video unmuted."


def volume_up():
    page = browser.start()

    page.keyboard.press("ARROWUP")

    return True, "Volume increased."


def volume_down():
    page = browser.start()

    page.keyboard.press("ARROWDOWN")

    return True, "Volume decreased."


def fullscreen():
    page = browser.start()

    page.keyboard.press("f")

    return True, "Full screen enabled."


def exit_fullscreen():
    page = browser.start()

    page.keyboard.press("ESC")

    return True, "Full screen closed."


def skip_ad():
    page = browser.start()

    selectors = [
        ".ytp-skip-ad-button",
        ".ytp-ad-skip-button",
        ".ytp-ad-skip-button-modern"
    ]

    for selector in selectors:
        try:
            button = page.locator(selector).first

            if button.is_visible(timeout=1000):
                button.click()

                return True, "I skipped the available ad."

        except Exception:
            continue

    return False, "There isn't a visible Skip Ad button right now."