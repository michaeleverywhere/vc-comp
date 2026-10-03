#!/usr/bin/env python3
"""DCVC portfolio scraper -> dcvc_companies.json
Source: https://www.dcvc.com/companies/ — server-rendered company-card articles.
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.dcvc.com/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "dcvc_companies.json")
PRIMARY = "DCVC"

SECTOR_MAP = {
    "computational-bio-and-chem": "Computational Bio & Chem",
    "agriculture": "Agriculture",
    "energy-climate": "Energy & Climate",
    "industrial-transformation": "Industrial Transformation",
    "computation": "Computation",
    "space": "Space",
    "autonomy": "Autonomy",
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for card in soup.select("article.company-card"):
        did = card.get("data-id")
        a = card.select_one("a[aria-label]")
        name = clean(a.get("aria-label")) if a else None
        if not name:
            continue
        key = (did or name).lower()
        if key in seen or name.lower() in {x for x in seen if not x.isdigit()}:
            # dedupe by name primarily
            pass
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        profile = clean(a.get("href")) if a else SOURCE_URL
        desc_el = card.select_one(".company-card__text, .company-card__description, p")
        desc = clean(desc_el.get_text()) if desc_el else None
        status_raw = card.get("data-status") or ""
        status = "Acquired" if "exits" in status_raw else "Active"
        sectors = []
        for part in (card.get("data-sector") or "").split(","):
            part = part.strip()
            if part and part != "all" and part in SECTOR_MAP:
                sectors.append(SECTOR_MAP[part])
            elif part and part != "all":
                sectors.append(part.replace("-", " ").title())
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": None,  # external website not on listing cards
            "status": status,
            "stage": None,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": profile or SOURCE_URL,
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
    print(f"  status: {Counter(r['status'] for r in out)}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
