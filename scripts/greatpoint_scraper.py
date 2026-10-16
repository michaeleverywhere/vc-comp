#!/usr/bin/env python3
"""GreatPoint Ventures portfolio scraper -> greatpoint_companies.json
Source: https://www.gpv.com/companies — Webflow list: logo link to the company
site (img alt = name) and a description paragraph that opens with the bold name.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.gpv.com/companies"
PRIMARY = "GreatPoint Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".w-dyn-item"):
        a = it.select_one("a[href^=http]")
        img = a.select_one("img[alt]") if a else None
        strong = it.select_one("p strong")
        name = clean(img.get("alt")) if img and clean(img.get("alt")) else (clean(strong.get_text()) if strong else None)
        ps = [clean(p.get_text(" ", strip=True)) for p in it.select("p")]
        desc = " ".join(p for p in ps if p) or None
        if not name:
            continue
        out.append(rec(name, desc, a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "greatpoint")


if __name__ == "__main__":
    main()
