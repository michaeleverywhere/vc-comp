#!/usr/bin/env python3
"""Garage Capital portfolio scraper -> garage_companies.json
Source: https://www.garage.vc/ — Webflow CMS list on the homepage: name, short
one-line description, website.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.garage.vc/"
PRIMARY = "Garage Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".w-dyn-item"):
        n = it.select_one(".text-block-8")
        d = it.select_one(".text-block-10")
        a = it.select_one("a[href^=http]")
        if not n:
            continue
        out.append(rec(n.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None,
                       a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "garage")


if __name__ == "__main__":
    main()
