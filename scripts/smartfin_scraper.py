#!/usr/bin/env python3
"""Smartfin portfolio scraper -> smartfin_companies.json
Source: https://smartfinvc.com/portfolio/ — WordPress/FacetWP grid (single
page, total_rows reported by FacetWP): company name (h2), "Country, Stage"
line and website link; each card links to a Smartfin detail page.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://smartfinvc.com/portfolio/"
PRIMARY = "Smartfin"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for art in soup.select("article"):
        h = art.find("h2")
        if not h:
            continue
        meta = h.find_next_sibling("div")
        site, country, stage = None, None, None
        if meta:
            a = meta.find("a", href=True)
            if a and a["href"].startswith("http") and not is_social(a["href"]):
                site = a["href"]
            first = clean(next(iter(meta.stripped_strings), "") or "")
            if first and "," in first:
                country, stage = [clean(x) for x in first.split(",", 1)]
        det = art.select_one("a[href*='/portfolio/']")
        out.append(rec(h.get_text(" ", strip=True), None, site, PRIMARY, SOURCE_URL, scraped_at,
                       country=country, stage=stage, detail_url=det["href"] if det else None))
    finish(out, "smartfin", ("company_url", "country", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
