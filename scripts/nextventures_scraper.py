#!/usr/bin/env python3
"""Next Ventures portfolio scraper -> nextventures_companies.json
Source: https://www.nextventures.com/portfolio — Webflow CMS portfolio cards (health, fitness and
nutrition fund): company name (logo alt), description, category and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.nextventures.com/portfolio"
PRIMARY = "Next Ventures"


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
    for it in s.select(".portfolio-item.w-dyn-item"):
        img = it.select_one(".portfolio-icon img")
        nm = clean(img.get("alt")) if img else None
        if not nm:
            continue
        cats = [txt(c) for c in it.select("[fs-list-field='category']") if txt(c)]
        out.append(rec(nm, txt(it.select_one(".portfolio-card__desc")), site(it.select_one("a.portfolio-card")), PRIMARY,
                       SOURCE_URL, scraped_at, sectors=cats))
    finish(out, "nextventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
