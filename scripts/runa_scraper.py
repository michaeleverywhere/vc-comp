#!/usr/bin/env python3
"""Runa Capital portfolio scraper -> runa_companies.json
Source: https://runacap.com/companies/ — WordPress company grid; each `.company__item` carries
data attributes (title, status, theme, location) plus a subtitle and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://runacap.com/companies/"
PRIMARY = "Runa Capital"


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
    for it in s.select(".company__item[data-title]"):
        nm = clean(it["data-title"])
        if not nm:
            continue
        st = clean(it.get("data-status"))
        theme = clean(it.get("data-theme"))
        a = it.select_one("a.link[href]")
        out.append(rec(nm, txt(it.select_one(".company-subtitle")), None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[theme] if theme else [], location=clean(it.get("data-location")), portfolio_status=st,
                       status="exited" if st and st.lower() == "exit" else None, detail_url=a["href"] if a else None))
    finish(out, "runa", ("description", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
