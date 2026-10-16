#!/usr/bin/env python3
"""Leadout Capital portfolio scraper -> leadout_companies.json
Source: https://www.leadoutcapital.com/portfolio — Webflow CMS portfolio list: company
name, website, year, description, sector and status attributes."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.leadoutcapital.com/portfolio"
PRIMARY = "Leadout Capital"


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
    for it in s.select(".w-dyn-item"):
        a = it.select_one("a.text-block")
        nm = txt(a)
        if not nm:
            continue
        sec = clean(it.get("data-sector"))
        st = clean(it.get("data-status"))
        out.append(rec(nm, txt(it.select_one(".text-block-3")), site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [],
                       year=year_of(txt(it.select_one(".text-block-2"))), portfolio_status=st,
                       status="exited" if st and ("exit" in st.lower() or "acqui" in st.lower()) else None))
    finish(out, "leadout", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
