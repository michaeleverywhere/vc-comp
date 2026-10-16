#!/usr/bin/env python3
"""Kinnevik portfolio scraper -> kinnevik_companies.json
Source: https://www.kinnevik.com/investments/ — "All companies" table: company
name, description, sector, invested year, HQ location and company page link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean, year_of
from _d50_common import rec, finish

ORIGIN = "https://www.kinnevik.com"
SOURCE_URL = ORIGIN + "/investments/"
PRIMARY = "Kinnevik"
SECTOR_MAP = {"health & bio": ["Health"], "consumer": ["Consumer"], "climate tech": ["Climate / Sustainability"],
              "climate": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch_response(SOURCE_URL).content, "html.parser")
    out = []
    for tr in soup.select("table.company-listing tr.item"):
        g = lambda c: clean(tr.select_one(c).get_text(" ", strip=True)) if tr.select_one(c) else None
        name = g(".__name")
        if not name:
            continue
        a = tr.select_one("a[href]")
        href = a["href"] if a else None
        sec = g("._sector")
        prior = sec == "Prior Strategies"  # Kinnevik's label for legacy holdings outside current strategy
        out.append(rec(name, g("._description"), None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec and not prior else None,
                       strategy="Prior Strategies" if prior else None,
                       sector_map=SECTOR_MAP, first_invested_year=year_of(g("._invested")), location=g("._location"),
                       detail_url=(ORIGIN + href) if href and href.startswith("/") else href))
    finish(out, "kinnevik", ("description", "first_invested_year", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
