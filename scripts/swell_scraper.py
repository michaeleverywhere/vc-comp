#!/usr/bin/env python3
"""Swell VC portfolio scraper -> swell_companies.json
Source: https://swell.vc/ — homepage portfolio cards: company name, one-line description,
sector tag and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://swell.vc/"
PRIMARY = "Swell VC"


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
    for a in s.select("a.portfolio-card"):
        nm = txt(a.select_one(".portfolio-name"))
        if not nm:
            continue
        secs = [txt(t) for t in a.select(".tag-sector") if txt(t)]
        out.append(rec(nm, txt(a.select_one(".portfolio-desc")), site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=secs))
    finish(out, "swell", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
