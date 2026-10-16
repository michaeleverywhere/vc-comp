#!/usr/bin/env python3
"""Moment Ventures portfolio scraper -> moment_companies.json
Source: https://www.momentventures.com/portfolio/ — WordPress portfolio boxes: company name, one-line
description or exit note, Acquired badge and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.momentventures.com/portfolio/"
PRIMARY = "Moment Ventures"


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
    for it in s.select(".portfolio-inner-box"):
        nm = txt(it.select_one(".overlay-btn-box h3"))
        if not nm:
            continue
        p = txt(it.select_one(".overlay-btn-box p"))
        acq = it.select_one(".status-acquired") is not None
        a = it.select_one("a[href]")
        out.append(rec(nm, p, None, PRIMARY, SOURCE_URL, scraped_at, status="acquired" if acq else None,
                       detail_url=a["href"] if a else None))
    finish(out, "moment", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
