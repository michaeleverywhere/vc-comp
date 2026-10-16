#!/usr/bin/env python3
"""Sawari Ventures portfolio scraper -> sawari_companies.json
Source: https://sawariventures.com/portfolio/ — Elementor text blocks: bold
linked company name followed by a description paragraph.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://sawariventures.com/portfolio/"
PRIMARY = "Sawari Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select(".elementor-widget-container p strong a[href]"):
        box = a.find_parent(class_="elementor-widget-container")
        ps = [clean(p.get_text(" ", strip=True)) for p in box.select("p")]
        name = clean(a.get_text(" ", strip=True))
        desc = " ".join(p for p in ps if p and p != name) or None
        out.append(rec(name, desc, a["href"], PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "sawari")


if __name__ == "__main__":
    main()
