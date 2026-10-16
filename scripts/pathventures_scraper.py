#!/usr/bin/env python3
"""Path Ventures portfolio scraper -> pathventures_companies.json
Source: https://www.path.vc/portfolio — portfolio list rows: company name, one-line description
and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.path.vc/portfolio"
PRIMARY = "Path Ventures"


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
    for li in s.select("li.wash"):
        a = li.find("a", href=True)
        spans = li.select("a > span")
        nm = txt(spans[0]) if spans else None
        if not nm:
            continue
        out.append(rec(nm, txt(spans[1]) if len(spans) > 1 else None, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "pathventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
