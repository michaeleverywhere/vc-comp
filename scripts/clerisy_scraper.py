#!/usr/bin/env python3
"""Clerisy portfolio scraper -> clerisy_companies.json
Source: https://clerisy.com/ — the page's own embedded portfolio JSON
(<script id="data-portfolio">): company name, domain (-> website) and Clerisy's category
label (Beverage / Wellness / Food / Media ...)."""
import os, re, sys, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://clerisy.com/"
PRIMARY = "Clerisy"
SECTOR_MAP = {"beverage": ["CPG", "Consumer"], "wellness": ["Health", "Consumer"], "food": ["CPG", "Consumer"],
              "media": ["Gaming / Media / Entertainment"], "media & entertainment": ["Gaming / Media / Entertainment"], "events": ["Gaming / Media / Entertainment"],
              "lifestyle": ["Consumer"], "entertainment": ["Gaming / Media / Entertainment"], "retail": ["Consumer"], "fitness": ["Health", "Consumer"], "sports": ["Consumer"],
              "golf": ["Consumer"], "digital commerce": ["Consumer"], "tech & services": [], "home": ["Consumer"], "apparel": ["Consumer"], "beauty": ["CPG", "Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    m = re.search(r'<script type="application/json" id="data-portfolio">(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("FATAL: data-portfolio JSON not found")
    out = []
    for it in json.loads(m.group(1)).get("items", []):
        name = clean(it.get("name"))
        if not name:
            continue
        dom_ = clean(it.get("domain"))
        tag = clean(it.get("tag") or it.get("category"))
        out.append(rec(name, None, f"https://{dom_}" if dom_ else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[tag] if tag else [], sector_map=SECTOR_MAP))
    if len(out) < 5:
        raise SystemExit(f"FATAL: only {len(out)} Clerisy companies")
    finish(out, "clerisy", ("company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
