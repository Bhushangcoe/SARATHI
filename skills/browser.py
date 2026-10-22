from urllib.parse import quote_plus

from core.browser_manager import browser


def open_url(url: str):
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    browser.open(url)

    return True, f"Opened {url}."


def search_web(query: str):
    url = f"https://www.google.com/search?q={quote_plus(query)}"

    browser.open(url)

    return True, f"I searched Google for {query}."