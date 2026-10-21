#!/usr/bin/env python3
"""SP Ventures portfolio scraper -> spventures_companies.json
Source: https://spventures.com.br/portfolio/ — AgFoodTech / ClimateTech VC (Brazil); JetEngine listing
grid rendered client-side (read via headless Chrome): one listing item per portfolio company — company
names only (descriptions sit behind per-company pop-ups that are not in the page)."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://spventures.com.br/portfolio/"
PRIMARY = "SP Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=50000), "html.parser")
    out = []
    for it in s.select("div.jet-listing-grid__item"):
        h = it.select_one("h2.elementor-heading-title")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if name:
            out.append(rec(name, None, None, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} SP Ventures companies")
    finish(out, "spventures", ("everywhere_tags",))


if __name__ == "__main__":
    main()
