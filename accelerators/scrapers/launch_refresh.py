"""LAUNCH Accelerator refresh (never-remove). Cohorts LA26-LA36 from the site's JS bundle
(rendered on launchaccelerator.co/companies); LA37 (Cohort 37, September 2026) from the
yearbook feed the /companies page itself loads (notion-yearbook-37). The 19 launch.co logo
companies are not re-scraped here and are left untouched. Never removes a company."""
import datetime, json, os, re, subprocess, sys, requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA_DIR, UA
from list_backfill_oct8 import rec

TODAY = datetime.date.today().isoformat()
P = os.path.join(DATA_DIR, "launch_companies.json")
D = json.load(open(P)); old = D["companies"]
home = requests.get("https://launchaccelerator.co/", headers=UA, timeout=30).text
js = re.search(r'src="(/assets/index-[^"]+\.js)"', home).group(1)
s = requests.get("https://launchaccelerator.co" + js, headers=UA, timeout=60).text
st = s.find('{id:"la36",label:"LA36"'); k = s.rfind("[", 0, st); depth, i = 0, k
while True:
    c = s[i]
    if c == "[": depth += 1
    elif c == "]":
        depth -= 1
        if depth == 0: break
    elif c == '"':
        i += 1
        while s[i] != '"':
            if s[i] == "\\": i += 1
            i += 1
    i += 1
open("/tmp/la_cohorts.js", "w").write("module.exports=" + s[k:i + 1])
cohorts = json.loads(subprocess.check_output(["node", "-e", 'process.stdout.write(JSON.stringify(require("/tmp/la_cohorts.js")))']))
api = re.search(r'"(https://[a-z0-9]+\.supabase\.co)",\w+=`\$\{\w+\}(/functions/v1/notion-yearbook-37)`', s)
feed = (api.group(1) + api.group(2)) if api else "https://rjbqjotgcddypxbzxixh.supabase.co/functions/v1/notion-yearbook-37"
y = requests.get(feed, headers={**UA, "Origin": "https://launchaccelerator.co", "Referer": "https://launchaccelerator.co/companies"}, timeout=30).json()
la37 = [{"name": c["name"].strip(), "description": (c.get("overview") or "").strip(), "website": (c.get("website") or "").strip(),
         "team": "; ".join(f.get("name", "") for f in c.get("founders", []) if isinstance(f, dict) and f.get("name"))} for c in y["companies"]]
cohorts = [{"label": "LA37", "companies": la37}] + [c for c in cohorts if c["label"] != "LA37"]

def site(u):
    u = (u or "").strip()
    if u and not u.startswith("http"): u = "https://" + u
    return u

byname = {o["name"].strip().lower(): o for o in old}
seen, added, supp = set(), [], 0
for co in cohorts:
    lab = co["label"]; latest = lab == "LA37"
    for c in co["companies"]:
        key = c["name"].strip().lower()
        if key in seen: continue
        seen.add(key)
        o = byname.get(key)
        if o is None:
            r = rec(name=c["name"].strip(), description=c.get("description", ""), website=site(c.get("website")), team=c.get("team", ""),
                    date=f"LAUNCH {lab}", investors="LAUNCH Accelerator", source="LAUNCH",
                    source_url="https://launchaccelerator.co/companies",
                    batch_date="2026-09" if latest else "", batch_date_precision="month (Cohort 37 · September 2026)" if latest else "",
                    most_recent_batch=latest)
            r.update(listed_on_site=True, first_seen=TODAY, last_seen=TODAY)
            old.append(r); byname[key] = r; added.append((lab, r["name"]))
        else:
            for f, v in (("description", c.get("description")), ("website", site(c.get("website"))), ("team", c.get("team"))):
                if v and not o.get(f): o[f] = v; supp += 1
            if not o.get("date", "").startswith("LAUNCH LA"):
                pass
            if o.get("listed_on_site") is False:
                o["relisted_date"] = TODAY
            o["listed_on_site"] = True; o["last_seen"] = TODAY
delisted = []
for o in old:
    if o.get("date", "").startswith("LAUNCH LA") and o["name"].strip().lower() not in seen and o.get("listed_on_site") is not False:
        o["listed_on_site"] = False; o["delisted_date"] = TODAY; delisted.append(o["name"])
for o in old:
    o["most_recent_batch"] = o.get("date") == "LAUNCH LA37"
D["companies"] = old; D["count"] = len(old)
json.dump(D, open(P, "w"), ensure_ascii=False, indent=1)
print(json.dumps({"count": len(old), "added": added, "supplemented_fields": supp, "delisted": delisted}, indent=1))
