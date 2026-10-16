#!/usr/bin/env python3
"""Necessary Ventures portfolio scraper -> necessary_companies.json
Source: https://www.necessary.vc/portfolio — Framer site; portfolio cards (repeated per breakpoint,
deduplicated) with company name, one-line description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.necessary.vc/portfolio"
PRIMARY = "Necessary Ventures"


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
    for a in s.select("a[href]"):
        nm = txt(a.select_one("[data-framer-name='Company Name']"))
        if not nm:
            continue
        out.append(rec(nm, txt(a.select_one("[data-framer-name='Company Description']")), site(a), PRIMARY, SOURCE_URL,
                       scraped_at))
    finish(out, "necessary", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
