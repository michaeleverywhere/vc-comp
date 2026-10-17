#!/usr/bin/env python3
"""Ironspring Ventures portfolio scraper -> ironspring_companies.json
Source: https://ironspring.com/portfolio-companies/ — Portfolio grid: company name and one-line description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://ironspring.com/portfolio-companies/"
PRIMARY = "Ironspring Ventures"


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
    seen = set()
    for f in s.select("figcaption"):
        nm = txt(f.select_one("h2"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        out.append(rec(nm.replace("\xa0", " "), txt(f.select_one("p")), None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "ironspring", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
