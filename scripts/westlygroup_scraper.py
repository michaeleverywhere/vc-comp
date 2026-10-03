#!/usr/bin/env python3
"""Westly Group portfolio scraper -> westlygroup_companies.json
Source: https://westlygroup.com/wp-json/wp/v2/portfolio
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, HEADERS, TIMEOUT

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://westlygroup.com/portfolio/"
API = "https://westlygroup.com/wp-json/wp/v2/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "westlygroup_companies.json")
PRIMARY = "Westly Group"


def fetch_all():
    page, rows = 1, []
    while True:
        r = requests.get(API, params={"per_page": 100, "page": page}, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        rows.extend(batch)
        total_pages = int(r.headers.get("X-WP-TotalPages") or 1)
        if page >= total_pages:
            break
        page += 1
    return rows


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    posts = fetch_all()
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in posts:
        title = p.get("title") or {}
        name = clean(title.get("rendered") if isinstance(title, dict) else title)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        meta = p.get("meta") or {}
        website = clean(meta.get("westly_company_url"))
        desc = clean(meta.get("westly_description") or meta.get("westly_tagline")) or None
        badge = clean(meta.get("westly_badge"))
        status = "Active"
        if badge and badge.lower() in ("exited", "acquired", "exit"):
            status = "Acquired"
        elif badge and badge.lower() in ("public", "ipo"):
            status = "Public"
        # category from class_list
        sectors = []
        for c in p.get("class_list") or []:
            if c.startswith("portfolio-category-") and c != "portfolio-category-":
                sectors.append(c.replace("portfolio-category-", "").replace("-", " ").title())
        profile = clean(p.get("link")) or SOURCE_URL
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": None,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": profile,
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
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
