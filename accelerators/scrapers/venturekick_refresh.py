"""Venture Kick refresh (never-remove). Listing: /tmp/vk_items.json produced by
venturekick_cdp_list.py with the site's own 'show more' endpoint paged to the end (2026-10-26:
835 listings). Details for new profiles: vk_details.json from venturekick_cdp_details.py.
Companies no longer on the public listing are kept and marked listed_on_site=false."""
import datetime, html, json, os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import DATA_DIR, tags
TODAY = datetime.date.today().isoformat()
P = os.path.join(DATA_DIR, "venturekick_companies.json")
D = json.load(open(P)); old = D["companies"]
items = json.load(open(sys.argv[1])); det = json.load(open(sys.argv[2]))
RENAMES = {"https://www.venturekick.ch/simmy--simcase": "https://www.venturekick.ch/simcase"}
byurl = {o["source_url"].lower(): o for o in old}
byname = {o["name"].strip().lower(): o for o in old}
seen, added, renamed = set(), [], []
for url, name, blurb in items:
    url = html.unescape(url)
    o = byurl.get(url.lower()) or byname.get(name.strip().lower())
    if o is None and url in RENAMES:
        o = byurl.get(RENAMES[url].lower())
        if o:
            o["former_name"] = o["name"]; o["name"] = name; o["source_url"] = url; renamed.append((o["former_name"], name))
    if o is None:
        d = det.get(url, {}); t = d.get("text", "")
        lines = [l.strip() for l in t.split("\n") if l.strip()]
        desc = lines[1] if len(lines) > 1 and not lines[1].startswith("Incorporated") else blurb
        inc = re.search(r"Incorporated:\s*\d{2}\.\d{2}\.(\d{4})", t); hq = re.search(r"Headquarter:\s*(.+)", t)
        try: i = lines.index("Support:"); vert = [l for l in lines[i+1:] if l]
        except ValueError: vert = []
        vert = list(dict.fromkeys(vert))
        links = [l for l in d.get("links", []) if l and l.startswith("http") and "venturekick" not in l]
        li = next((l for l in links if "linkedin.com/company" in l), "")
        web = next((l for l in links if "linkedin.com" not in l), "")
        o = dict(name=name, description=desc, website=web, team="", round="", amount_raised="", date="",
                 verticals="; ".join(vert), investors="Venture Kick", source="Venture Kick", everywhere_tags=[],
                 source_url=url, location=(hq.group(1).strip() + ", Switzerland") if hq else "", linkedin_url=li,
                 founded=inc.group(1) if inc else "", funding_rounds=[], grants=[])
        o["everywhere_tags"] = tags.classify(o["name"], o["description"], o["verticals"] or None)
        o["first_seen"] = TODAY
        old.append(o); byurl[url.lower()] = o; added.append(name)
    if o.get("listed_on_site") is False: o["relisted_date"] = TODAY
    o["listed_on_site"] = True; o["last_seen"] = TODAY; seen.add(id(o))
delisted = []
for o in old:
    if id(o) not in seen and o.get("listed_on_site") is not False:
        o["listed_on_site"] = False; o["delisted_date"] = TODAY; delisted.append(o["name"])
D["companies"] = old; D["count"] = len(old)
json.dump(D, open(P, "w"), ensure_ascii=False, indent=1)
print(json.dumps({"count": len(old), "added": added, "renamed": renamed, "delisted_n": len(delisted), "delisted_sample": delisted[:12]}, indent=1, ensure_ascii=False))
