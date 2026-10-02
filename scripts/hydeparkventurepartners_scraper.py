#!/usr/bin/env python3
"""Hyde Park Venture Partners portfolio scraper -> hydeparkventurepartners_companies.json
Source: https://hydeparkvp.com/companies.html — embedded company-card grid.
"""
import json, os, sys
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://hydeparkvp.com/companies.html"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "hydeparkventurepartners_companies.json")
PRIMARY = "Hyde Park Venture Partners"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for card in soup.select(".company-card"):
        name_el = card.select_one(".company-name")
        name = clean(name_el.get_text()) if name_el else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc_el = card.select_one(".company-desc")
        desc = clean(desc_el.get_text()) if desc_el else None
        tag_el = card.select_one(".company-type-tag")
        type_tag = clean(tag_el.get_text()) if tag_el else None
        data_sectors = (card.get("data-sectors") or "").split()
        sectors = []
        if type_tag:
            sectors.append(type_tag)
        for s in data_sectors:
            if s and s not in sectors and s.lower() != "exits":
                sectors.append(s)
        website = None
        location = None
        partner_since = None
        sector_label = None
        for st in card.select(".company-stat-item"):
            spans = st.select("span")
            if len(spans) < 2:
                continue
            label = clean(spans[0].get_text())
            val = clean(spans[1].get_text())
            if label == "Website":
                a = spans[1].select_one("a[href]")
                website = clean(a["href"]) if a else (f"https://{val}" if val and "." in val else None)
            elif label == "HQ":
                location = val
            elif label == "Partner Since":
                partner_since = val
            elif label == "Sector":
                sector_label = val
                if val and val not in sectors:
                    sectors.append(val)
        if not website:
            for a in card.select("a[href^='http']"):
                website = clean(a["href"])
                break
        status = "Exited" if "Exits" in data_sectors else "Active"
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": None,
            "location": location,
            "investment_year": partner_since,
            "sectors": sectors or None,
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
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")


if __name__ == "__main__":
    main()
