#!/usr/bin/env python3
"""Raed Ventures portfolio scraper -> raed_companies.json
Source: https://raed.vc/portfolio/ — server-rendered list of `a.list__item`
cards: company name (h3), description, country, category and year; each
links to a Raed detail page.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://raed.vc/portfolio/"
PRIMARY = "Raed Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select("a.list__item"):
        nm = txt(a.select_one(".list__item-name"))
        if not nm:
            continue
        cat = txt(a.select_one(".list__item-type"))
        out.append(rec(nm, txt(a.select_one(".list__item-text")), None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[cat] if cat else [], country=txt(a.select_one(".list__item-country")),
                       year=year_of(txt(a.select_one(".list__item-date")) or ""), detail_url=a.get("href")))
    finish(out, "raed", ("description", "country", "year", "everywhere_tags"))


if __name__ == "__main__":
    main()
