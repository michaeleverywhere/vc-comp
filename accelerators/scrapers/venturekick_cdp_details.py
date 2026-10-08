import json, subprocess, sys, time, urllib.request, websocket, signal
port=9334
lst=json.load(open('vk_list.json'))
p = subprocess.Popen(["google-chrome","--headless=new","--no-sandbox","--disable-gpu",f"--remote-debugging-port={port}","--user-data-dir=/tmp/cdpprof2",
   "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36","about:blank"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
try:
    for _ in range(50):
        try: tabs=json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json")); break
        except Exception: time.sleep(0.3)
    ws=websocket.create_connection([t for t in tabs if t["type"]=="page"][0]["webSocketDebuggerUrl"],timeout=600,suppress_origin=True)
    n=[0]
    def call(m,**pr):
        n[0]+=1; ws.send(json.dumps({"id":n[0],"method":m,"params":pr}))
        while True:
            x=json.loads(ws.recv())
            if x.get("id")==n[0]: return x.get("result")
    call("Page.enable"); call("Page.navigate",url="https://www.venturekick.ch/portfolio?profilesEntry=1"); time.sleep(6)
    res={}
    try: res=json.load(open('vk_details.json'))
    except Exception: pass
    todo=[x['url'] for x in lst if x['url'] not in res]
    for k in range(0,len(todo),40):
        chunk=todo[k:k+40]
        js="""(async (urls)=>{const out={};const one=async(u)=>{try{const r=await fetch(u,{credentials:'include'});const h=await r.text();
          const d=new DOMParser().parseFromString(h,'text/html');const a=d.querySelector('article.startup-detail')||d.body;
          out[u]={text:(a.innerText||a.textContent||'').slice(0,6000),links:[...a.querySelectorAll('a[href]')].map(x=>x.getAttribute('href')),
                  comments:(h.match(/<!-- (www\\.[^ ]+|https?:[^ ]+) -->/g)||[]).slice(0,3)};}catch(e){out[u]={err:String(e)}}};
          for(let i=0;i<urls.length;i+=4){await Promise.all(urls.slice(i,i+4).map(one));await new Promise(r=>setTimeout(r,300));}return out;})(%s)""" % json.dumps(chunk)
        r=call("Runtime.evaluate",expression=js,awaitPromise=True,returnByValue=True)
        res.update((r or {}).get("result",{}).get("value") or {})
        json.dump(res,open('vk_details.json','w'))
        print(len(res),flush=True)
finally:
    p.send_signal(signal.SIGTERM)
