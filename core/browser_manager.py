from pathlib import Path
from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent.parent
PROFILE_DIR = BASE_DIR / "browser_data"


class BrowserManager:

    def __init__(self):
        self.playwright = None
        self.context = None
        self.page = None

    def start(self):
        if self.page:
            return self.page

        PROFILE_DIR.mkdir(exist_ok=True)

        self.playwright = sync_playwright().start()

        self.context = self.playwright.chromium.launch_persistent_context(
            user_data_dir=str(PROFILE_DIR),
            headless=False,
            viewport={"width": 1280, "height": 800},
            args=[
                "--disable-notifications"
            ]
        )

        if self.context.pages:
            self.page = self.context.pages[0]
        else:
            self.page = self.context.new_page()

        return self.page

    def open(self, url: str):
        page = self.start()

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        return page

    def current_page(self):
        return self.start()

    def close(self):
        try:
            if self.context:
                self.context.close()

            if self.playwright:
                self.playwright.stop()

        except Exception:
            pass

        self.page = None
        self.context = None
        self.playwright = None


browser = BrowserManager()