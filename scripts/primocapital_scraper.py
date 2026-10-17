#!/usr/bin/env python3
"""Primo Capital portfolio scraper -> primocapital_companies.json
Source: https://www.primo.capital/portfolio — Webflow/Finsweet list: company name,
description, strategy (Digital / Space / Health / Climate) and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.primo.capital/portfolio"
PRIMARY = "Primo Capital"


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
    for it in s.select(".list-element"):
        nm = txt(it.select_one("h3.heading")) or txt(it.select_one("h3"))
        if not nm:
            continue
        strat = [txt(x) for x in it.select("[fs-cmsfilter-field='strategies']") if txt(x)]
        a = it if it.name == "a" else it.select_one("a[href]")
        href = a.get("href") if a else None
        out.append(rec(nm, txt(it.select_one(".list-description")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=strat,
                       detail_url=urljoin(SOURCE_URL, href) if href else None))
    finish(out, "primocapital", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
