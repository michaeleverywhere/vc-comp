#!/usr/bin/env python3
"""G2 Venture Partners portfolio scraper -> g2vp_companies.json
Source: https://www.g2vp.com/portfolio — Webflow CMS `.portfolio-item` cards:
company name (h3), website link and industry (Finsweet fs-list-field="cat").
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.g2vp.com/portfolio"
PRIMARY = "G2 Venture Partners"
SECTOR_MAP = {"energy": ["Climate / Sustainability"], "mobility": ["Transportation / Mobility"],
              "manufacturing": ["Deeptech / Robotics / AR/VR"], "agriculture": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".portfolio-item"):
        h = it.select_one(".portfolio-name")
        if not h:
            continue
        a = it.select_one("a[href]")
        href = a["href"] if a else ""
        cats = [clean(c.get_text(" ", strip=True)) for c in it.select("[fs-list-field='cat']")]
        out.append(rec(h.get_text(" ", strip=True), None, href if href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[c for c in cats if c], sector_map=SECTOR_MAP))
    finish(out, "g2vp", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
