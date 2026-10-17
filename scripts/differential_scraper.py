#!/usr/bin/env python3
"""Differential Ventures portfolio scraper -> differential_companies.json
Source: https://www.differential.vc/portfolio — a Squarespace blog collection read via
its own ?format=json view (paged with nextPageOffset when present): company name,
excerpt (description), categories (sector, investment theme and status: Active /
Acquired / Inactive / Betaworks Accelerator) and the website, taken as the first
external link in the post body that is not part of the shared footer/carousel links
repeated across posts."""
import os, re, sys, collections
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, html_text
from _d50_common import rec, finish

SOURCE_URL = "https://www.differential.vc/portfolio"
PRIMARY = "Differential Ventures"
STATUS = {"Active": "active", "Acquired": "acquired", "Inactive": "inactive"}
NON_SECTOR = set(STATUS) | {"All", "Betaworks Accelerator"}
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "cyber security & privacy": ["Cybersecurity"],
              "mlops & platforms": ["Dev Tools / Cloud"], "advancing the ml tech stack": ["Dev Tools / Cloud"],
              "engineering and infrastructure": ["Dev Tools / Cloud"], "responsible data management": ["Data & Analytics"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    items, url = [], SOURCE_URL + "?format=json"
    for _ in range(20):
        d = fetch(url, as_json=True)
        items += d.get("items") or []
        pg = d.get("pagination") or {}
        if not pg.get("nextPage"):
            break
        url = f"{SOURCE_URL}?format=json&offset={pg['nextPageOffset']}"
    links = lambda x: re.findall(r'href="(https?://[^"]+)"', x.get("body") or "")
    freq = collections.Counter(l for x in items for l in set(links(x)))
    out = []
    for x in items:
        name = clean(x.get("title"))
        if not name:
            continue
        site = next((l for l in links(x) if freq[l] <= 2 and not is_social(l)
                     and "crunchbase" not in l and "differential.vc" not in l), None)
        cats = [clean(c) for c in (x.get("categories") or []) if clean(c)]
        st = next((STATUS[c] for c in ("Acquired", "Inactive", "Active") if c in cats), None)
        sectors = [c for c in cats if c not in NON_SECTOR]
        out.append(rec(name, html_text(x.get("excerpt")), site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sectors, sector_map=SECTOR_MAP, status=st,
                       program="Betaworks Accelerator" if "Betaworks Accelerator" in cats else None,
                       detail_url="https://www.differential.vc" + x["fullUrl"] if x.get("fullUrl") else None))
    finish(out, "differential", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
