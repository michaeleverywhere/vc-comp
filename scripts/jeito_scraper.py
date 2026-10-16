#!/usr/bin/env python3
"""Jeito Capital portfolio scraper -> jeito_companies.json
Source: https://www.jeito.life/en/portfolio/ — WordPress (Divi Nexter blurbs):
company name (h2.dnxt-blurb-heading), therapeutic area (post-heading) and a
financing note (blurb description, e.g. rounds raised).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.jeito.life/en/portfolio/"
PRIMARY = "Jeito Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for b in soup.select(".dnxt-blurb-container"):
        h = b.select_one(".dnxt-blurb-heading")
        if not h or not clean(h.get_text()):
            continue
        area = b.select_one(".dnxt-blurb-post-heading")
        note = b.select_one(".dnxt-blurb-description")
        area = clean(area.get_text(" ", strip=True)) if area else None
        out.append(rec(h.get_text(" ", strip=True), None, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[area] if area else [], therapeutic_area=area,
                       financing=clean(note.get_text(" ", strip=True)) if note else None))
    finish(out, "jeito", ("therapeutic_area", "financing", "everywhere_tags"))


if __name__ == "__main__":
    main()
