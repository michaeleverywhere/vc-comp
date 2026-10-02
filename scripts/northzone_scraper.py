#!/usr/bin/env python3
"""Northzone portfolio scraper -> northzone_companies.json
Source: https://northzone.com/portfolio — Webflow company list items.
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://northzone.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "northzone_companies.json")
PRIMARY = "Northzone"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "lxml")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select(".filters5_company-list-item, .w-dyn-item"):
        name_el = it.select_one('[fs-cmsfilter-field="name"]')
        if not name_el:
            continue
        name = clean(name_el.get_text())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc_el = it.select_one(".text-color-secondary")
        desc = clean(desc_el.get_text()) if desc_el else None
        href = None
        a = it.select_one("a[href]")
        if a:
            href = a.get("href")
            if href and not href.startswith("http"):
                href = urljoin(SOURCE_URL, href)
        website = None
        for a2 in it.select("a[href^='http']"):
            if "northzone" not in a2["href"]:
                website = clean(a2["href"])
                break
        # industries from filter attrs if present
        sectors = []
        for el in it.select('[fs-cmsfilter-field="industry"], [fs-cmsfilter-field="industries"]'):
            t = clean(el.get_text())
            if t:
                sectors.append(t)
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": "Active",
            "stage": None,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": href or SOURCE_URL,
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
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
