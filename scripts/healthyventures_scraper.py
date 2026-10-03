#!/usr/bin/env python3
"""Healthy Ventures portfolio scraper -> healthyventures_companies.json
Source: https://healthy.vc/portfolio — Webflow collection items.
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://healthy.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "healthyventures_companies.json")
PRIMARY = "Healthy Ventures"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select(".collection-item.w-dyn-item, .w-dyn-item"):
        img = it.select_one("img[alt]")
        name = clean(img.get("alt")) if img and img.get("alt") else None
        if not name or name.lower() in seen:
            continue
        if name.lower() in ("healthy ventures", "logo"):
            continue
        seen.add(name.lower())
        copy = it.select_one(".portco-copy")
        desc = clean(copy.get_text(" ", strip=True)) if copy else None
        website = None
        for a in it.select("a[href^='http']"):
            href = a["href"]
            if "healthy.vc" in href or "webflow" in href or "website-files" in href:
                continue
            website = clean(href)
            break
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": "Active",
            "stage": None,
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
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
