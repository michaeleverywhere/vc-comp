#!/usr/bin/env python3
"""Icehouse Ventures portfolio scraper -> icehouseventures_companies.json
Source: https://jobs.icehouseventures.co.nz/companies — Icehouse Ventures' own portfolio board (Getro-hosted, linked
as "Jobs" from icehouseventures.co.nz; the main portfolio page is a logo wall without names). The board's company
list is read from the same public JSON search endpoint the page itself calls (Getro collection 943, no key):
company name, description, website domain, stage, location and the board's visible industry tags."""
import os, sys, time
from datetime import datetime, timezone
import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, HEADERS
from _d50_common import rec, finish

SOURCE_URL = "https://jobs.icehouseventures.co.nz/companies"
API = "https://api.getro.com/api/v2/collections/943/search/companies"
PRIMARY = "Icehouse Ventures"


def page(n):
    h = {**HEADERS, "Content-Type": "application/json", "Accept": "application/json",
         "Origin": "https://jobs.icehouseventures.co.nz", "Referer": SOURCE_URL}
    for attempt in range(1, 4):
        try:
            r = requests.post(API, json={"hitsPerPage": 50, "page": n, "filters": "", "query": ""}, headers=h, timeout=45)
            r.raise_for_status()
            return r.json()["results"]
        except requests.RequestException as e:
            last = e
            time.sleep(2 * attempt)
    raise SystemExit(f"FATAL: Getro page {n}: {last}")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    hits, n = [], 0
    while True:
        res = page(n)
        hits += res.get("companies") or []
        if not res.get("companies") or len(hits) >= res.get("count", 0):
            break
        n += 1
        time.sleep(0.4)
    out = []
    for c in hits:
        name = clean(c.get("name"))
        if not name:
            continue
        dom = clean(c.get("domain"))
        locs = list(dict.fromkeys(clean(x) for x in c.get("locations") or [] if clean(x)))
        st = clean(c.get("stage"))
        out.append(rec(name, c.get("description"), f"https://{dom}" if dom else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=c.get("visible_industry_tags") or [], stage=st.replace("_", " ").title() if st else None,
                       location="; ".join(locs) or None))
    if len(out) < 150:
        raise SystemExit(f"FATAL: only {len(out)} Icehouse companies")
    finish(out, "icehouseventures", ("description", "company_url", "sectors", "stage", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
