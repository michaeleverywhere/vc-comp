#!/usr/bin/env python3
"""Airwing portfolio scraper -> airwing_companies.json
Source: https://airwing.vc/portfolio/ — portfolio tiles: company name, one-line
description and website (the server sometimes returns a truncated page, so it is re-fetched)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://airwing.vc/portfolio/"
PRIMARY = "Airwing"


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
    import time
    for _ in range(6):
        s = soup_of(SOURCE_URL)
        if s.select(".portfolio-item"):
            break
        time.sleep(3)
    for it in s.select(".portfolio-item"):
        a = it.select_one(".content a[href]") or it.select_one("a[href]")
        nm = txt(it.select_one("h3"))
        if not nm:
            continue
        out.append(rec(nm, txt(it.select_one("h4")), site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "airwing", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
