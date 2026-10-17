#!/usr/bin/env python3
"""Shorooq portfolio scraper -> shorooq_companies.json
Source: https://www.shorooq.com/portfolio — Portfolio list: company name, category, country and
tagline."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.shorooq.com/portfolio"
PRIMARY = "Shorooq"


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
    for it in s.select("div.pf-item button.pf-row"):
        nm = txt(it.select_one(".pf-row-name"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        cat = txt(it.select_one(".pf-row-cat"))
        out.append(rec(nm, txt(it.select_one(".pf-row-tagline")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [],
                       location=txt(it.select_one(".pf-row-country"))))
    finish(out, "shorooq", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
