#!/usr/bin/env python3
"""Hemisphere Ventures portfolio scraper -> hemisphere_companies.json
Source: https://www.hemisphere.com/companies.html — companies grid: company name and category
(class filter)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.hemisphere.com/companies.html"
PRIMARY = "Hemisphere Ventures"


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
    names = {"b2b": "B2B", "space": "Space", "biotechnology": "Biotechnology", "consumer": "Consumer", "hardware": "Hardware"}
    for it in s.select("div.company-logo"):
        nm = txt(it.find("p")) or (clean(it.find("img").get("alt")) if it.find("img") else None)
        if not nm:
            continue
        cats = [names.get(c, c.replace("-", " ").title()) for c in (it.get("class") or []) if c not in ("company-logo", "space-holder")]
        a = it.find_parent("a")
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=cats))
    finish(out, "hemisphere", ("everywhere_tags",))


if __name__ == "__main__":
    main()
