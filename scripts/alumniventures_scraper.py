#!/usr/bin/env python3
"""Alumni Ventures portfolio scraper -> alumniventures_companies.json
Source: https://www.av.vc/portfolio — Next.js page whose server-rendered __NEXT_DATA__
carries the firm's full published portfolio list (the filterable grid): company name,
description, website, named co-investors, AV's region / stage / sector tags and the
AV funds that hold the company."""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.av.vc/portfolio"
PRIMARY = "Alumni Ventures"
SECTOR_MAP = {"healthtech": ["Health"], "life sciences": ["BioTech", "Health"], "fintech": ["FinTech / Insurance"],
              "consumer": ["Consumer"], "cleantech": ["Climate / Sustainability"], "mobility": ["Transportation / Mobility"],
              "food & ag": ["CPG"], "cybersecurity": ["Cybersecurity"], "ar / vr": ["Deeptech / Robotics / AR/VR"],
              "iot & advanced manufacturing": ["Deeptech / Robotics / AR/VR"], "big data": ["Data & Analytics"],
              "real estate technology": ["PropTech"], "web3": ["Web3 / Crypto"], "tmt": ["Gaming / Media / Entertainment"],
              "saas": ["Dev Tools / Cloud"], "marketingtech": [], "ai & ml": [], "industrials": [], "other": []}


def find_companies(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k == "companies" and isinstance(v, list) and v and isinstance(v[0], dict) and "info" in v[0]:
                return v
            r = find_companies(v)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_companies(v)
            if r:
                return r
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("FATAL: no __NEXT_DATA__ on av.vc/portfolio")
    cs = find_companies(json.loads(m.group(1))) or []
    out, seen = [], set()
    for c in cs:
        info, tags = c.get("info") or {}, c.get("tags") or {}
        name = clean(c.get("name") or info.get("name"))
        if not name or (name.lower(), c.get("slug")) in seen:
            continue
        seen.add((name.lower(), c.get("slug")))
        url = (info.get("url") or "").strip() or None
        sec = (tags.get("sector") or {}).get("name")
        co = [x.strip() for x in (info.get("coinvestors") or "").split(",") if x.strip()]
        out.append(rec(name, clean(info.get("description")), url if url and not is_social(url) else None, PRIMARY,
                       SOURCE_URL, scraped_at, sectors=[sec] if sec else [], sector_map=SECTOR_MAP, sector_label=sec,
                       location=(tags.get("geo") or {}).get("name"), stage=(tags.get("stage") or {}).get("name"),
                       co_investors=co, av_funds=[f.get("name") for f in (c.get("funds") or []) if f.get("name")]))
    if len(out) < 1000:
        raise SystemExit(f"FATAL: only {len(out)} Alumni Ventures companies")
    finish(out, "alumniventures", ("description", "company_url", "sector_label", "location", "stage", "co_investors", "everywhere_tags"))


if __name__ == "__main__":
    main()
