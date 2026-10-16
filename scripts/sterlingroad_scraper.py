#!/usr/bin/env python3
"""Sterling Road portfolio scraper -> sterlingroad_companies.json
Source: https://sterlingroad.com/portfolio — portfolio tiles grouped by year: company name,
category, 'Since <year>' and website link."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://sterlingroad.com/portfolio"
PRIMARY = "Sterling Road"


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
    for it in s.select(".pf-tile"):
        nm = txt(it.select_one(".pf-wash-name"))
        if not nm:
            continue
        cat = txt(it.select_one(".pf-wash-cat"))
        out.append(rec(nm, None, site(it.find("a", href=True)), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[cat] if cat else [], year_invested=year_of(txt(it.select_one(".pf-wash-since")) or "")))
    finish(out, "sterlingroad", ("company_url", "year_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
