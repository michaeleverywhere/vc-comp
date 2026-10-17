#!/usr/bin/env python3
"""Royal Street Ventures portfolio scraper -> royalstreet_companies.json
Source: https://www.royalstreet.vc/portfolio/ — portfolio accordion: company name,
description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.royalstreet.vc/portfolio/"
PRIMARY = "Royal Street Ventures"


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
    for li in s.select("li.accordion-group"):
        nm = txt(li.select_one(".accordion-target"))
        if nm:
            out.append(rec(nm, txt(li.select_one(".portfolio-description")), site(li.select_one("a.btn-2")), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "royalstreet", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
