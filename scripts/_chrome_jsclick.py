"""Rendered-DOM fetch that presses a page's own "view more" / "show more" control via DOM click()
(Daily 20, 2026-10-21).

Some portfolio pages draw the button label without text, or keep a cookie banner over it, so the
mouse-event clicking in _chrome_click.dom_loadmore cannot reach it. dom_jsclick(url, find_js) opens the
same public page a visitor sees in system google-chrome (headless, local DevTools port), calls .click()
on the element returned by find_js until it disappears or the item count (count_js) stops growing,
then returns the rendered HTML. No API keys or private endpoints.
"""
import json
import subprocess
import tempfile
import time
import urllib.request

import websocket

import _chrome_click as cc


def dom_jsclick(url, find_js, count_js, settle_s=8, step_s=1.5, max_clicks=300, stale_limit=4, scroll=False):
    """find_js: JS expression returning the button element (or null). count_js: JS number expression.
    scroll=True: when the button is gone, keep scrolling to the bottom (pages that switch from a
    button to infinite scroll) until the count stops growing."""
    port, prof = cc._free_port(), tempfile.mkdtemp(prefix="chrome-jsclick-")
    proc = subprocess.Popen([cc._chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--window-size=1440,4000",
                             f"--user-agent={cc.UA}", f"--remote-debugging-port={port}", f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        tabs = []
        for _ in range(50):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2))
                if any(t.get("type") == "page" for t in tabs):
                    break
            except Exception:
                time.sleep(0.3)
        page = next(t for t in tabs if t.get("type") == "page")
        ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
        tab = cc._Tab(ws)
        tab.call("Page.enable")
        tab.call("Page.navigate", url=url)
        time.sleep(settle_s)
        last, stale = tab.js(count_js), 0
        click = f"(() => {{ const b = ({find_js}); if (!b || b.offsetParent === null) return false; b.click(); return true; }})()"
        for _ in range(max_clicks):
            if not tab.js(click):
                if not scroll:
                    break
                tab.js("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(step_s)
            now = tab.js(count_js)
            stale = stale + 1 if now == last else 0
            if stale >= stale_limit:
                break
            last = now
        html = tab.js("document.documentElement.outerHTML") or ""
        ws.close()
        return html
    finally:
        proc.kill()
        proc.wait(timeout=10)
