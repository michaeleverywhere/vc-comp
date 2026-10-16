#!/usr/bin/env python3
"""TTV Capital portfolio scraper -> ttv_companies.json
Source: https://ttvcapital.com/portfolio/ — WordPress (PowerPack content
grid) company posts: name, fund, "Visit Website" link, detail page, and
post category classes (active / exited / IPO / unicorn).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://ttvcapital.com/portfolio/"
PRIMARY = "TTV Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".pp-content-post"):
        h = it.select_one(".pp-content-grid-post-title")
        if not h or not clean(h.get_text()):
            continue
        cls = set(it.get("class") or [])
        meta = it.select_one(".pp-content-grid-post-meta")
        site = det = None
        for a in it.find_all("a", href=True):
            if "/company/" in a["href"] and "ttvcapital.com" in a["href"]:
                det = det or a["href"]
            elif a["href"].startswith("http") and not is_social(a["href"]) and "Visit Website" in a.get_text():
                site = a["href"]
        status = "public" if "category-ipo" in cls else ("exited" if "category-exited-companies" in cls else
                                                          ("active" if "category-active-companies" in cls else None))
        out.append(rec(h.get_text(" ", strip=True), None, site, PRIMARY, SOURCE_URL, scraped_at,
                       fund=clean(meta.get_text(" ", strip=True)) if meta else None, status=status,
                       unicorn=True if "category-unicorns" in cls else None, detail_url=det))
    finish(out, "ttv", ("company_url", "fund", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
