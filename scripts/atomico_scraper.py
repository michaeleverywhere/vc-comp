#!/usr/bin/env python3
"""Atomico portfolio scraper -> atomico_companies.json
Source: https://careers.atomico.com/companies — Getro collection 36986 public search API; company name, description, domain, stage, industry tags."""
import os, sys, time
from datetime import datetime, timezone
import requests
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, HEADERS
from _d50_common import rec, finish
SOURCE_URL = "https://careers.atomico.com/companies"
API = "https://api.getro.com/api/v2/collections/36986/search/companies"
PRIMARY = "Atomico"

def page(n):
    h = {**HEADERS, "Content-Type": "application/json", "Accept": "application/json",
         "Origin": "https://careers.atomico.com", "Referer": SOURCE_URL}
    for attempt in range(1, 4):
        try:
            r = requests.post(API, json={"hitsPerPage": 50, "page": n, "filters": "", "query": ""}, headers=h, timeout=45)
            r.raise_for_status(); return r.json()["results"]
        except requests.RequestException as e:
            last = e; time.sleep(2 * attempt)
    raise SystemExit(f"FATAL: Getro page {n}: {last}")

def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    hits, n = [], 0
    while True:
        res = page(n); hits += res.get("companies") or []
        if not res.get("companies") or len(hits) >= res.get("count", 0): break
        n += 1; time.sleep(0.3)
    out = []
    for c in hits:
        name = clean(c.get("name"))
        if not name or name.lower() == PRIMARY.lower(): continue
        dom = clean(c.get("domain")); st = clean(c.get("stage"))
        out.append(rec(name, c.get("description"), f"https://{dom}" if dom else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=c.get("visible_industry_tags") or [], stage=st.replace("_", " ").title() if st else None))
    finish(out, "atomico", ("description", "company_url", "sectors", "stage", "everywhere_tags"))
if __name__ == "__main__":
    main()
