#!/usr/bin/env python3
"""Lattice Fund portfolio scraper -> lattice_companies.json
Source: https://lattice.fund/portfolio — static cards: name linked to the website
and a one-line description.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://lattice.fund/portfolio"
PRIMARY = "Lattice Fund"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch_response(SOURCE_URL).content, "html.parser")
    out = []
    for c in soup.select(".pcard"):
        h = c.find("h3")
        if not h:
            continue
        a = h.find("a", href=True)
        p = c.find("p")
        out.append(rec(h.get_text(" ", strip=True), clean(p.get_text(" ", strip=True)) if p else None,
                       a["href"] if a and a["href"].startswith("http") else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "lattice", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
