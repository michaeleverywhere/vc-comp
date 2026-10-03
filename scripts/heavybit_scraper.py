#!/usr/bin/env python3
"""Heavybit portfolio scraper -> heavybit_companies.json
Source: Sanity API project 50q6fr1p — organization where portfolioCompany==true
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import quote

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, HEADERS, TIMEOUT

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.heavybit.com/portfolio"
API = "https://50q6fr1p.api.sanity.io/v2021-10-21/data/query/production"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "heavybit_companies.json")
PRIMARY = "Heavybit"

QUERY = '''*[_type=="organization" && portfolioCompany==true]{
  name, description, status, joined,
  "website": coalesce(website, url, homepage, link, siteUrl),
  about
}'''


def rich_text(blocks):
    if not blocks:
        return None
    parts = []
    for b in blocks:
        if not isinstance(b, dict):
            continue
        for c in b.get("children") or []:
            if isinstance(c, dict) and c.get("text"):
                parts.append(c["text"])
    return clean(" ".join(parts)) if parts else None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    r = requests.get(API, params={"query": QUERY}, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    companies = r.json().get("result") or []
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for c in companies:
        name = clean(c.get("name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(c.get("description")) or rich_text(c.get("about"))
        website = clean(c.get("website"))
        status_raw = (c.get("status") or "").lower()
        status = "Active"
        if status_raw in ("exited", "acquired", "exit"):
            status = "Acquired"
        elif status_raw in ("public", "ipo"):
            status = "Public"
        elif status_raw == "stealth":
            status = "Active"  # still active, stealth is not a lead-status enum we use
        first_invested = clean(c.get("joined"))  # ISO date on site — keep as date string, not funding round
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": None,
            "first_invested": None,  # joined is a date, not a funding-round label
            "joined_date": first_invested,  # preserve site field without inventing stage
            "everywhere_tags": classify(name, desc)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
