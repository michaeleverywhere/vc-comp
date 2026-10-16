#!/usr/bin/env python3
"""Link Ventures portfolio scraper -> link_companies.json
Source: https://www.linkventures.com/portfolio — Webflow CMS portfolio rows (Finsweet fields): company
name, category, fund and year invested."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.linkventures.com/portfolio"
PRIMARY = "Link Ventures"


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
    for it in s.select(".portfolio-cont-grid-w"):
        f = {e["fs-cmsfilter-field"]: txt(e) for e in it.select("[fs-cmsfilter-field]")}
        nm = f.get("Name")
        if not nm:
            continue
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[f["Category"]] if f.get("Category") else [],
                       fund=f.get("Fund"), year_invested=year_of(f.get("Year") or "")))
    finish(out, "link", ("fund", "year_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
