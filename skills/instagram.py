import time
from urllib.parse import quote_plus

from core.browser_manager import browser


INSTAGRAM_URL = "https://www.instagram.com"


def open_instagram():
    page = browser.open(INSTAGRAM_URL)

    return True, "Instagram is open."


def open_profile():
    page = browser.start()

    page.goto(
        f"{INSTAGRAM_URL}/",
        wait_until="domcontentloaded",
        timeout=30000
    )

    return True, "Instagram profile area is open."


def open_messages():
    page = browser.start()

    page.goto(
        f"{INSTAGRAM_URL}/direct/inbox/",
        wait_until="domcontentloaded",
        timeout=30000
    )

    return True, "Instagram messages are open."


def open_notifications():
    page = browser.start()

    try:
        page.goto(
            f"{INSTAGRAM_URL}/",
            wait_until="domcontentloaded",
            timeout=30000
        )

        return True, "Instagram is open. You can access notifications from the interface."

    except Exception:
        return False, "I couldn't open Instagram notifications."


def search(query: str):
    page = browser.start()

    encoded = quote_plus(query)

    page.goto(
        f"{INSTAGRAM_URL}/explore/search/?q={encoded}",
        wait_until="domcontentloaded",
        timeout=30000
    )

    time.sleep(2)

    return True, f"I searched Instagram for {query}."


def scroll_down():
    page = browser.start()

    page.mouse.wheel(0, 700)

    return True, "Scrolled down."


def scroll_up():
    page = browser.start()

    page.mouse.wheel(0, -700)

    return True, "Scrolled up."


def open_reels():
    page = browser.start()

    page.goto(
        f"{INSTAGRAM_URL}/reels/",
        wait_until="domcontentloaded",
        timeout=30000
    )

    return True, "Instagram Reels are open."


def next_reel():
    page = browser.start()

    page.keyboard.press("ARROWDOWN")

    return True, "Moving to the next reel."


def previous_reel():
    page = browser.start()

    page.keyboard.press("ARROWUP")

    return True, "Moving to the previous reel."


def pause_reel():
    page = browser.start()

    page.keyboard.press("SPACE")

    return True, "Reel paused."


def resume_reel():
    page = browser.start()

    page.keyboard.press("SPACE")

    return True, "Reel resumed."


def like():
    page = browser.start()

    try:
        page.keyboard.press("l")

        return True, "I attempted to like the current post."

    except Exception:
        return False, "I couldn't like the current post."


def save():
    return False, "Save automation needs to be connected to the current Instagram interface."


def follow():
    return False, "Follow automation needs to be connected to the current Instagram interface."


def unfollow():
    return False, "Unfollow automation needs to be connected to the current Instagram interface."


def send_message(username: str, message: str):
    page = browser.start()

    page.goto(
        f"{INSTAGRAM_URL}/direct/inbox/",
        wait_until="domcontentloaded",
        timeout=30000
    )

    time.sleep(2)

    return (
        False,
        f"I opened Instagram messages, but I won't send the message automatically yet. "
        f"Target: {username}. Message: {message}"
    )


def create_post(path: str, caption: str = ""):
    return (
        False,
        "The Instagram post workflow needs the current upload interface and should "
        "stop at preview before publishing."
    )


def create_story(path: str, text: str = ""):
    return (
        False,
        "The Instagram story workflow needs the current upload interface and should "
        "stop at preview before publishing."
    )


def create_reel(path: str, caption: str = ""):
    return (
        False,
        "The Instagram Reel workflow needs the current upload interface and should "
        "stop at preview before publishing."
    )