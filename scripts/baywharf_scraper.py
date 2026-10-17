#!/usr/bin/env python3
"""Bay Wharf Capital portfolio scraper -> baywharf_companies.json
Source: https://www.baywharfcapital.com/portfolio — portfolio grid: company name, website and
description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.baywharfcapital.com/portfolio"
PRIMARY = "Bay Wharf Capital"


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
    for it in s.select("div.grid-item"):
        a = it.select_one("h3.grid-item-title a") or it.select_one("h3.grid-item-title")
        nm = txt(a)
        if nm:
            out.append(rec(nm, txt(it.select_one(".grid-item-content")), site(a if a.name == "a" else None), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "baywharf", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
