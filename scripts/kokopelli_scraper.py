#!/usr/bin/env python3
"""Kokopelli Capital portfolio scraper -> kokopelli_companies.json
Source: https://kokopelli.vc/the-portfolio/ — "Kokofolio" grid: company name and detail page;
website from each company page's Visit Site link."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://kokopelli.vc/the-portfolio/"
PRIMARY = "Kokopelli Capital"


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
    items = [(txt(h), (h.get("href") or "").strip()) for h in s.select("h3.post-title a") if txt(h)]
    pages = fetch_many([u for _, u in items if u])
    for nm, u in items:
        web = None
        if pages.get(u):
            a = BeautifulSoup(pages[u], "html.parser").select_one(".portfolio-link a[href], a.button[href]")
            web = site(a)
        out.append(rec(nm, None, web, PRIMARY, SOURCE_URL, scraped_at, detail_url=u or None))
    finish(out, "kokopelli", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
