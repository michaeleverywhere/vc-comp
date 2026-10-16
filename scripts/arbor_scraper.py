#!/usr/bin/env python3
"""Arbor Ventures portfolio scraper -> arbor_companies.json
Source: https://www.arborventures.com/our-portfolio — Webflow CMS partner cards: company name (logo alt
text), status badge (e.g. Exit), description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.arborventures.com/our-portfolio"
PRIMARY = "Arbor Ventures"


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
    for it in s.select(".card-partner-wrapper"):
        img = it.select_one(".card-partner img")
        nm = clean(img.get("alt")) if img else None
        if not nm:
            continue
        st = txt(it.select_one(".partner-status"))
        out.append(rec(nm, txt(it.select_one("p.partner-blurb")), site(it.select_one("a.partner-blurb")), PRIMARY,
                       SOURCE_URL, scraped_at, portfolio_status=st, status="exited" if st and st.lower() == "exit" else None))
    finish(out, "arbor", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
