#!/usr/bin/env python3
"""Third Sphere portfolio scraper -> thirdsphere_companies.json
Source: https://thirdsphere.com/portfolio/all/ — WordPress climate-tech portfolio grid: company name
(link title / tile caption) and website link."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://thirdsphere.com/portfolio/all/"
PRIMARY = "Third Sphere"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(fetch(url), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for it in s.select(".portfolio-item-listing"):
        a = it.find("a", href=True)
        nm = clean(a.get("title")) if a and a.get("title") else txt(it.select_one(".title .px-1"))
        if not nm:
            continue
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "thirdsphere", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
