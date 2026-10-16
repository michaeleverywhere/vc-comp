#!/usr/bin/env python3
"""Felix Capital portfolio scraper -> felix_companies.json
Source: https://www.felixcap.com/ — Squarespace portfolio summary grid: company
name and website link only (the site publishes no descriptions in the grid).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.felixcap.com/"
PRIMARY = "Felix Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".summary-item"):
        t = it.select_one(".summary-title")
        a = it.select_one("a[data-title]") or it.find("a", href=True)
        name = clean(t.get_text(" ", strip=True)) if t else (a.get("data-title") if a else None)
        if not name:
            continue
        href = a.get("href") if a else None
        d = clean(a.get("data-description")) if a else None
        out.append(rec(name, d or None, href if href and href.startswith("http") and "felixcap" not in href else None,
                       PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "felix", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
