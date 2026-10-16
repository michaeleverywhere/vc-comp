#!/usr/bin/env python3
"""Z47 (formerly Matrix Partners India) portfolio scraper -> z47_companies.json
Source: https://www.z47.com/portfolio — Webflow CMS list: company name, one-line
description, sector class (enterprise / AI / consumer / financial / B2B) and
company page link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean
from _d50_common import rec, finish

ORIGIN = "https://www.z47.com"
SOURCE_URL = ORIGIN + "/portfolio"
PRIMARY = "Z47"
SECTORS = {"is-enterprise": "Enterprise", "is-ai": "AI", "is-consumer": "Consumer", "is-financial": "Financial Services", "is-b2b": "B2B"}
SECTOR_MAP = {"consumer": ["Consumer"], "financial services": ["FinTech / Insurance"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".portfolio_item"):
            n = it.select_one('[fs-cmsfilter-field="name"]')
            img = it.select_one("img[alt]")
            name = clean(n.get_text()) if n and clean(n.get_text()) else (clean(img.get("alt")) if img else None)
            if not name:
                continue
            inner = it.select_one(".portfolio_inner-item")
            cls = inner.get("class") if inner else []
            d = it.select_one(".w-richtext")
            a = it.select_one("a[href^='/portfolio/']")
            out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None, None, PRIMARY, SOURCE_URL, scraped_at,
                           sectors=[SECTORS[c] for c in cls if c in SECTORS], sector_map=SECTOR_MAP,
                           detail_url=ORIGIN + a["href"] if a else None))
    finish(out, "z47", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
