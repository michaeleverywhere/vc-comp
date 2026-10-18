#!/usr/bin/env python3
"""Offline Ventures portfolio scraper -> offlineventures_companies.json
Source: https://offline.vc/portfolio — client-rendered (Vite/React) page; the full
portfolio list ships inside the site's own /assets/index-*.js bundle as an array of
{id, name, website, shortDescription, longDescription, sector, featured,
acquisitionInfo?} objects, read here without executing any JS."""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://offline.vc/portfolio"
PRIMARY = "Offline Ventures"
SECTOR_MAP = {"deep tech": ["Deeptech / Robotics / AR/VR"], "consumer": ["Consumer"], "fintech": ["FinTech / Insurance"],
              "health": ["Health"], "b2b": [], "ai": [], "web3": ["Web3 / Crypto"], "crypto": ["Web3 / Crypto"]}
OBJ = re.compile(r'\{id:"[a-z0-9-]+",name:"(?:[^"\\]|\\.)*",.*?featured:![01][^}]*\}', re.S)


def field(o, k):
    m = re.search(r'[,{]' + k + r':"((?:[^"\\]|\\.)*)"', o)
    if not m:
        return None
    try:
        return clean(json.loads('"' + m.group(1) + '"'))
    except ValueError:
        return clean(m.group(1))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    js = re.search(r'src="(/assets/index-[^"]+\.js)"', html)
    if not js:
        raise SystemExit("FATAL: no index bundle on offline.vc/portfolio")
    bundle = fetch(urljoin(SOURCE_URL, js.group(1)))
    out, seen = [], set()
    for o in OBJ.findall(bundle):
        name = field(o, "name")
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        web = field(o, "website")
        short, long = field(o, "shortDescription"), field(o, "longDescription")
        sec = field(o, "sector")
        acq = field(o, "acquisitionInfo")
        out.append(rec(name, short or long, web if web and web.startswith("http") and not is_social(web) else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [], sector_map=SECTOR_MAP,
                       sector_label=sec, long_description=long if long and long != short else None,
                       featured="featured:!0" in o, exit_note=acq,
                       status="acquired" if acq and re.search(r"acqui", acq, re.I) else ("exited" if acq else "active")))
    if len(out) < 80:
        raise SystemExit(f"FATAL: only {len(out)} Offline Ventures companies")
    finish(out, "offlineventures", ("description", "company_url", "sector_label", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
