#!/usr/bin/env python3
"""Rosecliff Ventures portfolio scraper -> rosecliff_companies.json
Source: https://rosecliff.com/portfolio — portfolio grid: company name, website and
description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://rosecliff.com/portfolio"
PRIMARY = "Rosecliff Ventures"


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
    for it in s.select("div.item.cover"):
        nm = txt(it.find("h2"))
        if nm:
            out.append(rec(nm, txt(it.find("p")), site(it.select_one("a.company_link")), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "rosecliff", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
