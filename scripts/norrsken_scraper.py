#!/usr/bin/env python3
"""Norrsken VC portfolio scraper -> norrsken_companies.json
Source: https://www.norrsken.vc/portfolio — Webflow CMS `.sort-item` cards
(paginated): name (h2), one-line description and Finsweet list fields
Country, Sector, Funding stage and Year of investment.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.norrsken.vc/portfolio"
PRIMARY = "Norrsken VC"
SECTOR_MAP = {"energy tech": ["Climate / Sustainability"], "climate tech": ["Climate / Sustainability"],
              "food tech": ["Climate / Sustainability"], "health tech": ["Health"], "edtech": ["Consumer"],
              "fintech": ["FinTech / Insurance"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    pages = webflow_pages(SOURCE_URL)
    pages = list(pages.values()) if isinstance(pages, dict) else pages
    out = []
    for html in pages:
        soup = BeautifulSoup(html, "html.parser")
        for e in soup.select(".w-condition-invisible"):
            e.decompose()
        for it in soup.select(".sort-item"):
            h = it.select_one(".portfolio-item-title h2")
            if not h:
                continue
            f = {e["fs-list-field"].lower(): clean(e.get_text(" ", strip=True)) for e in it.select("[fs-list-field]")}
            d = it.select_one(".portfolio-item-about p")
            a = it.select_one("a[href]")
            out.append(rec(h.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None, None, PRIMARY,
                           SOURCE_URL, scraped_at, sectors=[f["sector"]] if f.get("sector") else [], sector_map=SECTOR_MAP,
                           country=f.get("country"), stage=f.get("funding stage"),
                           first_invested_year=year_of(f.get("year of investment") or ""),
                           detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "norrsken", ("description", "country", "stage", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
