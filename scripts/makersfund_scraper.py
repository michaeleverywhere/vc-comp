#!/usr/bin/env python3
"""Makers Fund portfolio scraper -> makersfund_companies.json
Source: https://www.makersfund.com/portfolio — Next.js `__NEXT_DATA__` pageProps.companies
(name, founders, active/exited status + exit label, HQ location, category /
region CSS classes). Descriptions and websites are not published on the index.
Makers Fund is a games-only investor, so every company carries the Gaming tag.
"""
import os, re, sys, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, prune_substring_tags, apply_tag_overrides, carry_forward_descriptions
from _d20_common import write_out

SOURCE_URL = "https://www.makersfund.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "makersfund_companies.json")
PRIMARY = "Makers Fund"
CATS = {"content": "Content", "ecosystem": "Ecosystem", "platform": "Platform & Tools"}
REGIONS = {"americas": "Americas", "asia": "Asia", "emea": "EMEA"}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    comps = json.loads(m.group(1))["props"]["pageProps"]["companies"] if m else []
    out, seen = [], set()
    for c in comps:
        name = clean(re.sub(r"(?i)\s*-\s*a(?:c)?quired by .*$", "", c.get("title") or ""))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cls = (c.get("cls") or "").split()
        st = (c.get("status") or "").lower()
        label = clean(c.get("exited_label"))
        acquirer = None
        if label:
            mm = re.search(r"(?i)a(?:c)?quired by\s+(.+)", label)
            acquirer = clean(mm.group(1)) if mm else None
        out.append({
            "company_name": name,
            "description": None,
            "company_url": None,
            "founders": [clean(x) for x in re.split(r",|&| and ", c.get("founders") or "") if clean(x)],
            "location": clean(c.get("location")),
            "sectors": [CATS[k] for k in cls if k in CATS],
            "region": next((REGIONS[k] for k in cls if k in REGIONS), None),
            "site_status": st or None,
            "status": "active" if st == "active" else ("acquired" if acquirer else None),
            "exited": st == "exited",
            "exit_detail": label,
            "acquirer": acquirer,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    carry_forward_descriptions(out, OUT)
    for r in out:
        kw = [t for t in tags_for(r["company_name"], r["description"]) if t != "Gaming / Media / Entertainment"]
        r["everywhere_tags"] = (["Gaming / Media / Entertainment"] + kw)[:3]
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("founders", "location", "status", "description", "everywhere_tags"))


if __name__ == "__main__":
    main()
