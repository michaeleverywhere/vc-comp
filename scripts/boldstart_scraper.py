#!/usr/bin/env python3
"""Boldstart Ventures portfolio scraper -> boldstart_companies.json
Source: https://boldstart.vc/companies/ — category sections with company-row cards.
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://boldstart.vc/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "boldstart_companies.json")
PRIMARY = "Boldstart Ventures"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for row in soup.select(".company-row"):
        name_el = row.select_one(".company-name")
        if not name_el:
            continue
        name = clean(name_el.get_text())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc_el = row.select_one(".company-description")
        desc = clean(desc_el.get_text()) if desc_el else None
        year_el = row.select_one(".company-year")
        year = None
        if year_el:
            m = re.search(r"(19|20)\d{2}", year_el.get_text())
            if m:
                year = int(m.group(0))
        website = None
        a = row.select_one("a[href^='http']")
        if a and "boldstart" not in a["href"]:
            website = clean(a["href"])
        cat = None
        parent = row.find_parent(class_="company-category") or row.find_parent(class_=re.compile("category|section"))
        if parent:
            h = parent.find(["h2", "h3", "h4"])
            if h:
                cat = clean(h.get_text())
        sectors = [cat] if cat else []
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": "Active",
            "stage": None,
            "investment_year": year,
            "sectors": sectors,
            "everywhere_tags": classify(name, desc, sectors)[:4],
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
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
