#!/usr/bin/env python3
"""Orvel Ventures portfolio scraper -> orvel_companies.json
Source: https://www.orvel.vc/portfolio — portfolio cards: company name, country,
description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.orvel.vc/portfolio"
PRIMARY = "Orvel Ventures"


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
    for a in s.select("a[class$='_link']"):
        t = a.select_one("[class$='_title']")
        nm = txt(t)
        if not nm:
            continue
        out.append(rec(nm, txt(a.select_one("[class$='_description']")), site(a), PRIMARY, SOURCE_URL, scraped_at,
                       location=txt(a.select_one("[class$='_subtitle']"))))
    finish(out, "orvel", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
