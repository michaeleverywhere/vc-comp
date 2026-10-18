#!/usr/bin/env python3
"""firstminute capital portfolio scraper -> firstminute_companies.json
Source: https://www.firstminute.capital/portfolio — Next.js page whose company grid is
fetched client-side (not in the raw HTML), read from the rendered DOM via headless
Chrome (_chrome_dom.py): company name, firstminute's sector label(s) and the
geography label (UK and Europe / US / RoW ...). The site publishes no per-company
description or website."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.firstminute.capital/portfolio"
PRIMARY = "firstminute capital"
SECTOR_MAP = {"healthtech": ["Health"], "fintech": ["FinTech / Insurance"], "climatetech": ["Climate / Sustainability"],
              "deeptech": ["Deeptech / Robotics / AR/VR"], "developer tools": ["Dev Tools / Cloud"],
              "commercial open-source software": ["Dev Tools / Cloud"], "blockchain": ["Web3 / Crypto"],
              "gaming & media": ["Gaming / Media / Entertainment"], "consumer & marketplace": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=100000), "html.parser")
    out = []
    for card in s.select('[class*="styles_portfolio__"]'):
        h = card.select_one('h2[class*="styles_title"]')
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        cats = card.select('[class*="styles_categories__"] > div')
        sec = clean(cats[0].get_text(" ", strip=True)) if cats else None
        geo = clean(cats[1].get_text(" ", strip=True)) if len(cats) > 1 else None
        sectors = [clean(x) for x in (sec or "").split(",") if clean(x)]
        out.append(rec(name, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP,
                       sector_label=sec, geography=geo))
    if len(out) < 80:
        raise SystemExit(f"FATAL: only {len(out)} firstminute rows rendered")
    finish(out, "firstminute", ("sector_label", "geography", "everywhere_tags"))


if __name__ == "__main__":
    main()
