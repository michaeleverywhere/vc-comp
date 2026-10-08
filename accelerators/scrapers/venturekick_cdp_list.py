import json, subprocess, sys, time, urllib.request, websocket, os, signal
url, out, js_loop = sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ""
port = 9333
p = subprocess.Popen(["google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
     f"--remote-debugging-port={port}", "--user-data-dir=/tmp/cdpprof",
     "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36",
     "about:blank"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try:
            tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json")); break
        except Exception: time.sleep(0.3)
    ws_url = [t for t in tabs if t["type"] == "page"][0]["webSocketDebuggerUrl"]
    ws = websocket.create_connection(ws_url, timeout=120, suppress_origin=True)
    i = [0]
    def call(method, **params):
        i[0] += 1; ws.send(json.dumps({"id": i[0], "method": method, "params": params}))
        while True:
            m = json.loads(ws.recv())
            if m.get("id") == i[0]: return m.get("result")
    def ev(expr):
        r = call("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
        return (r or {}).get("result", {}).get("value")
    call("Page.enable"); call("Page.navigate", url=url); time.sleep(6)
    if js_loop:
        prev, stable = -1, 0
        for k in range(400):
            n = ev(js_loop)
            if n == prev: stable += 1
            else: stable = 0
            prev = n
            if stable >= 4: break
            time.sleep(1.5)
        print("final count", prev)
    open(out, "w").write(ev("document.documentElement.outerHTML") or "")
finally:
    p.send_signal(signal.SIGTERM)
