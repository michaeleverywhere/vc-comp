"""Headless-Chrome helpers (CDP) for accelerator portfolio pages that only render
in a real browser (JS apps, or hosts that serve an automatic browser check to
plain HTTP clients). Loads the accelerator's OWN public page only.

render(url, loop_js=None) -> rendered outerHTML
capture(url, rx) -> list of {url, body} for the page's own XHR/fetch responses
                    whose URL matches rx (the same data the page displays)
"""
from __future__ import annotations

import json
import re
import signal
import subprocess
import time
import urllib.request

import websocket

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"


class _Chrome:
    def __init__(self, port, prof):
        self.p = subprocess.Popen(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
                                   f"--remote-debugging-port={port}", f"--user-data-dir={prof}",
                                   f"--user-agent={UA}", "about:blank"],
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        tabs = None
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
                break
            except Exception:
                time.sleep(0.3)
        self.ws = websocket.create_connection([t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"],
                                              timeout=2, suppress_origin=True)
        self.i = 0

    def send(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        return self.i

    def recv(self):
        try:
            return json.loads(self.ws.recv())
        except Exception:
            return None

    def call(self, method, timeout=60, **params):
        i = self.send(method, **params)
        t0 = time.time()
        while time.time() - t0 < timeout:
            m = self.recv()
            if m and m.get("id") == i:
                return m.get("result")
        return None

    def close(self):
        try:
            self.p.send_signal(signal.SIGTERM)
            self.p.wait(10)
        except Exception:
            pass


def render(url, loop_js=None, settle=6, port=9341, prof="/tmp/cdp_render"):
    c = _Chrome(port, prof)
    try:
        c.call("Page.enable")
        c.call("Page.navigate", url=url)
        time.sleep(settle)
        ev = lambda e: ((c.call("Runtime.evaluate", expression=e, awaitPromise=True, returnByValue=True) or {})
                        .get("result", {}).get("value"))
        if loop_js:
            prev, stable = None, 0
            for _ in range(300):
                n = ev(loop_js)
                stable = stable + 1 if n == prev else 0
                prev = n
                if stable >= 4:
                    break
                time.sleep(1.5)
        return ev("document.documentElement.outerHTML") or ""
    finally:
        c.close()


def capture(url, rx, wait=25, port=9342, prof="/tmp/cdp_capture"):
    rx = re.compile(rx)
    c = _Chrome(port, prof)
    out, want, pending = [], {}, {}
    try:
        c.send("Network.enable")
        c.send("Page.navigate", url=url)
        t0 = time.time()
        while time.time() - t0 < wait:
            m = c.recv()
            if not m:
                continue
            if m.get("method") == "Network.responseReceived" and rx.search(m["params"]["response"]["url"]):
                want[m["params"]["requestId"]] = m["params"]["response"]["url"]
            elif m.get("method") == "Network.loadingFinished" and m["params"]["requestId"] in want:
                pending[c.send("Network.getResponseBody", requestId=m["params"]["requestId"])] = want[m["params"]["requestId"]]
            elif m.get("id") in pending:
                body = (m.get("result") or {}).get("body", "")
                if body:
                    out.append({"url": pending.pop(m["id"]), "body": body})
        return out
    finally:
        c.close()
