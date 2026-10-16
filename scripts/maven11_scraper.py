#!/usr/bin/env python3
"""Maven 11 portfolio scraper -> maven11_companies.json
Source: https://maven11.com/portfolios — Webflow list: category, name, bio,
year invested, website (popup per item).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://maven11.com/portfolios"
PRIMARY = "Maven 11"
SECTOR_MAP = {"infrastructure": ["Web3 / Crypto"], "defi": ["Web3 / Crypto", "FinTech / Insurance"],
              "gaming": ["Web3 / Crypto", "Gaming / Media / Entertainment"], "applications": ["Web3 / Crypto"],
              "middleware": ["Web3 / Crypto"], "cefi": ["Web3 / Crypto", "FinTech / Insurance"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".portfolio_item.w-dyn-item"):
        nm = it.select_one(".content_wrapper h1.clipped")
        if not nm:
            continue
        cat = it.select_one(".category_heading")
        bio = it.select_one(".scrollable_content")
        inv = None
        for d in it.select(".flex_wrapper > div"):
            hs = [clean(h.get_text()) for h in d.find_all("h1", recursive=False)]
            if hs and hs[0] == "INVESTED" and len(hs) > 1:
                inv = year_of(hs[1])
        w = it.select_one(".button_popup_wrapper a[href^=http]")
        c = clean(cat.get_text()) if cat else None
        out.append(rec(nm.get_text(" ", strip=True), bio.get_text(" ", strip=True) if bio else None, w["href"] if w else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[c.title()] if c else [], sector_map=SECTOR_MAP,
                       first_invested_year=inv))
    finish(out, "maven11", ("description", "company_url", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
