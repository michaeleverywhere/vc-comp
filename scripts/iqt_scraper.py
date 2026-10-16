#!/usr/bin/env python3
"""In-Q-Tel (IQT) portfolio scraper -> iqt_companies.json
Source: https://www.iqt.org/portfolio — Webflow CMS list (paginated
`?<hash>_page=N`); each `.ci-categories` item gives the company name linked to
its website, technology categories, location (region) and status. No
descriptions are published on the list.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.iqt.org/portfolio"
PRIMARY = "In-Q-Tel"
SECTOR_MAP = {"cyber": ["Cybersecurity"], "microelectronics & quantum": ["Deeptech / Robotics / AR/VR"],
              "space": ["Deeptech / Robotics / AR/VR"], "life sciences": ["BioTech"], "hardware": ["Deeptech / Robotics / AR/VR"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL, max_pages=80):
        for it in BeautifulSoup(html, "html.parser").select(".ci-categories.w-dyn-item"):
            nm = it.select_one(".cl-company")
            if not nm:
                continue
            a = it.select_one("a.lb-company-list[href]")
            href = a["href"] if a else ""
            cats = [clean(c.get_text(" ", strip=True)) for c in it.select(".text-category")]
            loc = it.select_one(".cl-location")
            st = clean(it.select_one(".cl-status").get_text(" ", strip=True)) if it.select_one(".cl-status") else None
            norm = {"active": "active", "exited": "exited"}.get((st or "").lower())
            out.append(rec(nm.get_text(" ", strip=True), None, href if href.startswith("http") and not is_social(href) else None,
                           PRIMARY, SOURCE_URL, scraped_at, sectors=cats, sector_map=SECTOR_MAP,
                           region=clean(loc.get_text(" ", strip=True)) if loc else None,
                           portfolio_status=st, status=norm))
    finish(out, "iqt", ("company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
