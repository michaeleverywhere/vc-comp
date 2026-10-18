"""Rendered-DOM fetch for JS-only portfolio pages (Daily 20, 2026-10-18).

dom(url) runs the system google-chrome headless (--dump-dom) and returns the page's
HTML *after* client-side rendering — the same public page a visitor sees, no API
keys or private endpoints. Used by scrapers whose portfolio is rendered by
Angular / React / Framer / Next client code and absent from the raw HTML.
"""
import os
import shutil
import subprocess

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _chrome():
    for c in (os.environ.get("CHROME_PATH"), "/usr/bin/google-chrome", shutil.which("google-chrome"),
              shutil.which("chromium"), shutil.which("chromium-browser")):
        if c and os.path.isfile(c):
            return c
    raise SystemExit("FATAL: google-chrome/chromium not found; required for this JS-rendered portfolio")


def dom(url, budget_ms=12000, tries=3, min_len=5000):
    """Rendered HTML of url (retries when the dump comes back empty/short)."""
    last = ""
    for _ in range(tries):
        try:
            p = subprocess.run([_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu",
                                "--hide-scrollbars", "--window-size=1440,4000",
                                f"--virtual-time-budget={budget_ms}", f"--user-agent={UA}", "--dump-dom", url],
                               capture_output=True, text=True, timeout=budget_ms / 1000 + 60)
            last = p.stdout or ""
        except subprocess.TimeoutExpired:
            last = ""
        if len(last) >= min_len:
            return last
    if not last:
        raise SystemExit(f"FATAL: empty rendered DOM for {url}")
    return last
