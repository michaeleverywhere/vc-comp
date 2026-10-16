#!/usr/bin/env python3
"""Canapi Ventures portfolio scraper -> canapi_companies.json
Source: https://canapi.com/portfolio — Webflow CMS investment cards: company name, one-line
description, status (e.g. Acquired) and detail page /investment/<slug>."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://canapi.com/portfolio"
PRIMARY = "Canapi Ventures"


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
    for a in s.select("a[investments-portfolio='link']"):
        nm = txt(a.find("h3"))
        if not nm:
            continue
        st = a.select_one("[fs-cmsfilter-field='status']")
        st = txt(st) if st and "w-dyn-bind-empty" not in (st.get("class") or []) else None
        out.append(rec(nm, txt(a.select_one(".t-18")), None, PRIMARY, SOURCE_URL, scraped_at, portfolio_status=st,
                       status="acquired" if st and "acqui" in st.lower() else ("public" if st and "ipo" in st.lower() else None),
                       detail_url=urljoin(SOURCE_URL, a["href"])))
    finish(out, "canapi", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
