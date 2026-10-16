#!/usr/bin/env python3
"""January Ventures portfolio scraper -> january_companies.json
Source: https://www.january.ventures/ — homepage founder grid (Webflow CMS): company
name, description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.january.ventures/"
PRIMARY = "January Ventures"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for it in s.select("div.founder-grid-item"):
        d = it.select(".info-top > div")
        nm = txt(d[0]) if d else None
        if not nm:
            continue
        out.append(rec(nm, txt(d[1]) if len(d) > 1 else None, site(it.select_one("a.button-text")), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "january", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
