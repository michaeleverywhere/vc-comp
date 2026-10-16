#!/usr/bin/env python3
"""Aavishkaar Capital portfolio scraper -> aavishkaar_companies.json
Source: https://aavishkaarcapital.in/portfolios/ — WordPress (The Grid) tiles;
each tile repeats the company name (h3) in image and caption headers.
Names only.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://aavishkaarcapital.in/portfolios/"
PRIMARY = "Aavishkaar Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for h in soup.select(".tgr-item-title h3"):
        nm = clean(h.get_text(" ", strip=True))
        if nm:
            out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "aavishkaar", ("everywhere_tags",))


if __name__ == "__main__":
    main()
