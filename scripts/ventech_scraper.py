#!/usr/bin/env python3
"""Ventech portfolio scraper -> ventech_companies.json
Source: https://www.ventechvc.com/our-companies — Webflow "All companies" list
(paginated): company name and one-line description per card.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.ventechvc.com/our-companies"
PRIMARY = "Ventech"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for c in soup.select(".all_companies_card_wrap"):
            h = c.find(["h2", "h3"])
            p = c.find("p")
            if not h:
                continue
            out.append(rec(h.get_text(" ", strip=True), clean(p.get_text(" ", strip=True)) if p else None, None,
                           PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "ventech", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
