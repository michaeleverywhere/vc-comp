"""Rendered-DOM fetch with "Load more" clicking for JS-paginated portfolio pages
(Daily 20, 2026-10-19).

dom_loadmore(url) starts the system google-chrome headless with a local DevTools port,
opens the same public page a visitor sees, clicks the page's own "Load more" button
(matched by its visible text, real mouse events) until it disappears or stops adding content, then returns
the rendered HTML. No API keys or private endpoints. Requires the websocket-client
package (import websocket) alongside google-chrome.
"""
import json
import os
import shutil
import socket
import subprocess
import tempfile
import time
import urllib.request

import websocket

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0 Safari/537.36")


def _chrome():
    for c in (os.environ.get("CHROME_PATH"), "/usr/bin/google-chrome", shutil.which("google-chrome"),
              shutil.which("chromium"), shutil.which("chromium-browser")):
        if c and os.path.isfile(c):
            return c
    raise SystemExit("FATAL: google-chrome/chromium not found; required for this JS-rendered portfolio")


def _free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


class _Tab:
    def __init__(self, ws):
        self.ws, self.i = ws, 0

    def call(self, method, **params):
        self.i += 1
        my = self.i
        self.ws.send(json.dumps({"id": my, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == my:
                return m.get("result", {})

    def js(self, expr):
        r = self.call("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=True)
        return (r.get("result") or {}).get("value")


LOCATE_JS = r"""
(() => {
  const rx = new RegExp(%s, 'i');
  const els = [...document.querySelectorAll('a,button,[role=button],span,div,p')]
    .filter(e => rx.test((e.innerText || '').trim()) && e.offsetParent !== null);
  if (!els.length) return null;
  const e = els[els.length - 1];
  e.scrollIntoView({block: 'center'});
  const b = e.getBoundingClientRect();
  if (!b.width || !b.height) return null;
  return [b.x + b.width / 2, b.y + b.height / 2];
})()
"""


def dom_loadmore(url, button_rx=r"^load more$", settle_s=8, step_s=2.5, max_clicks=60, count_js="document.body.innerHTML.length",
                 expand_selector=None, expand_wait_s=1.2):
    """Rendered HTML of url after clicking the "Load more" control until exhausted.

    With expand_selector, each visible element matching it is then clicked in turn (the
    page's own accordion / detail toggle) and a list of each element's outerHTML after its
    click (the expanded state) is returned instead of the page HTML."""
    port = _free_port()
    prof = tempfile.mkdtemp(prefix="chrome-click-")
    proc = subprocess.Popen([_chrome(), "--headless=new", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
                             "--window-size=1440,4000", f"--user-agent={UA}", f"--remote-debugging-port={port}",
                             f"--user-data-dir={prof}", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        tabs = None
        for _ in range(50):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json", timeout=2))
                if any(t.get("type") == "page" for t in tabs):
                    break
            except Exception:
                time.sleep(0.3)
        page = next(t for t in tabs if t.get("type") == "page")
        ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=60, suppress_origin=True)
        tab = _Tab(ws)
        tab.call("Page.enable")
        tab.call("Page.navigate", url=url)
        time.sleep(settle_s)
        last, stale = tab.js(count_js), 0
        for _ in range(max_clicks):
            xy = tab.js(LOCATE_JS % json.dumps(button_rx))
            if not xy:
                break
            for typ in ("mouseMoved", "mousePressed", "mouseReleased"):
                tab.call("Input.dispatchMouseEvent", type=typ, x=xy[0], y=xy[1], button="left", clickCount=1)
            time.sleep(step_s)
            now = tab.js(count_js)
            if now == last:
                stale += 1
                if stale >= 3:
                    break
            else:
                stale = 0
            last = now
        if expand_selector:
            sel = json.dumps(expand_selector)
            n = tab.js(f"[...document.querySelectorAll({sel})].filter(e => e.offsetParent !== null).length") or 0
            res = []
            for i in range(n):
                xy = tab.js(f"""(() => {{ const e = [...document.querySelectorAll({sel})].filter(e => e.offsetParent !== null)[{i}];
                    if (!e) return null; e.scrollIntoView({{block: 'center'}}); const b = e.getBoundingClientRect();
                    return [b.x + b.width / 2, b.y + Math.min(b.height / 2, 20)]; }})()""")
                if not xy:
                    continue
                for typ in ("mouseMoved", "mousePressed", "mouseReleased"):
                    tab.call("Input.dispatchMouseEvent", type=typ, x=xy[0], y=xy[1], button="left", clickCount=1)
                time.sleep(expand_wait_s)
                res.append(tab.js(f"""(() => {{ const e = [...document.querySelectorAll({sel})].filter(e => e.offsetParent !== null)[{i}];
                    return e ? e.outerHTML : null; }})()"""))
            ws.close()
            return res
        html = tab.js("document.documentElement.outerHTML") or ""
        ws.close()
        return html
    finally:
        proc.kill()
        proc.wait(timeout=10)
        shutil.rmtree(prof, ignore_errors=True)
