#!/usr/bin/env python3
"""Azolla Ventures portfolio scraper -> azolla_companies.json
Source: https://azollaventures.com/our-portfolio/ — WordPress (JetElements
images layout): company name (h5), short description (published as a predicate following the name,
e.g. "is decarbonizing shipping..."; kept verbatim) and website link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://azollaventures.com/our-portfolio/"
PRIMARY = "Azolla Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for c in soup.select(".jet-images-layout__inner"):
        h = c.select_one(".jet-images-layout__title")
        if not h or not clean(h.get_text()):
            continue
        name = h.get_text(" ", strip=True)
        d = c.select_one(".jet-images-layout__desc")
        desc = clean(d.get_text(" ", strip=True)) if d else None
        a = c.select_one("a[href]")
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        out.append(rec(name, desc, href, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "azolla", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
