#!/usr/bin/env python3
"""Premji Invest portfolio scraper -> premji_companies.json
Source: https://www.premjiinvest.com/portfolio — Webflow CMS list; each item embeds
a schema block (data-name, data-desc, data-url) plus stage (Growth/Early/Public),
status (Private / IPO/Public / Acquired), sector and geography fields.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean
from _d50_common import rec, finish

ORIGIN = "https://www.premjiinvest.com"
SOURCE_URL = ORIGIN + "/portfolio"
PRIMARY = "Premji Invest"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "healthcare": ["Health"], "consumer": ["Consumer"]}
STATUS = {"private": "active", "ipo/public": "ipo", "acquired": "acquired"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".portfolio---item"):
            sc = it.select_one(".portfolio-schema-item")
            img = it.select_one("img[alt]")
            name = clean(sc.get("data-name")) if sc else None
            name = name or (clean(img.get("alt")) if img else None)
            if not name:
                continue
            g = lambda f: [clean(x.get_text()) for x in it.select(f'[fs-cmsfilter-field="{f}"]') if clean(x.get_text())]
            status = (g("status") or [None])[0]
            stage = None
            for x in it.select(".hide .text-m"):
                if not x.get("fs-cmsfilter-field") and clean(x.get_text()):
                    stage = clean(x.get_text())
                    break
            a = it.select_one("a[href^='/portfolio/']")
            out.append(rec(name, clean(sc.get("data-desc")) if sc else None, (sc.get("data-url") or None) if sc else None,
                           PRIMARY, SOURCE_URL, scraped_at, sectors=g("sector"), sector_map=SECTOR_MAP,
                           stage=stage, portfolio_status=status, status=STATUS.get((status or "").lower(), (status or "").lower() or None),
                           location=", ".join(g("geography")) or None, detail_url=ORIGIN + a["href"] if a else None))
    finish(out, "premji", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
