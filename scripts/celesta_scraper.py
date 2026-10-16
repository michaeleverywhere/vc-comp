#!/usr/bin/env python3
"""Celesta Capital portfolio scraper -> celesta_companies.json
Source: https://www.celesta.vc/portfolio — Webflow CMS cards
(`.collection-item-12`): company name (h2), hover description, status label
(e.g. Exited), detail link and nested category list.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.celesta.vc/portfolio"
PRIMARY = "Celesta Capital"
SECTOR_MAP = {"semiconductors": ["Deeptech / Robotics / AR/VR"], "cybersecurity": ["Cybersecurity"],
              "data infrastructure": ["Data & Analytics"], "robotics": ["Deeptech / Robotics / AR/VR"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".collection-item-12.w-dyn-item"):
            h = it.select_one("a.port-card h2")
            if not h:
                continue
            a = it.select_one("a.port-card[href]")
            d = it.select_one(".port-hover .text-block-55")
            lab = it.select_one(".label-status div")
            st = clean(lab.get_text(" ", strip=True)) if lab else None
            cats = [clean(c.get_text(" ", strip=True)) for c in it.select("[fs-list-field=category]")]
            out.append(rec(h.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None, None,
                           PRIMARY, SOURCE_URL, scraped_at, sectors=list(dict.fromkeys(c for c in cats if c)),
                           sector_map=SECTOR_MAP, portfolio_status=st,
                           status={"exited": "exited", "active": "active", "exited — ipo": "ipo"}.get((st or "").lower()),
                           detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "celesta", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
