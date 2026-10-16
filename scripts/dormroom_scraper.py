#!/usr/bin/env python3
"""Dorm Room Fund portfolio scraper -> dormroom_companies.json
Source: https://www.dormroomfund.com/portfolio — Webflow CMS name list (`.portfolio-name-card`): company
name, website link and category."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.dormroomfund.com/portfolio"
PRIMARY = "Dorm Room Fund"


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
    for it in s.select(".portfolio-name-card"):
        a = it.select_one("a.portfolio-name_link")
        nm = txt(a)
        if not nm:
            continue
        cats = [txt(c) for c in it.select("[fs-list-field='category']") if txt(c)]
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=cats))
    finish(out, "dormroom", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
