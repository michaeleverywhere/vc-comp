#!/usr/bin/env python3
"""Great North Ventures portfolio scraper -> greatnorth_companies.json
Source: https://greatnorthventures.com/our-portfolio/ — Elementor portfolio tiles: company
name, Great North fund and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://greatnorthventures.com/our-portfolio/"
PRIMARY = "Great North Ventures"


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
    for h in s.select("h4"):
        nm = txt(h)
        w = h.find_parent(class_="elementor-widget")
        box = h.find_parent(class_="e-con")
        if not nm or not w or not box:
            continue
        nx = w.find_next_sibling(class_="elementor-widget")
        fund = txt(nx) if nx else None
        web = next((site(a) for a in box.select("a[href^=http]") if site(a) and "greatnorthventures.com" not in a["href"]), None)
        out.append(rec(nm, None, web, PRIMARY, SOURCE_URL, scraped_at, fund=fund if fund and "fund" in fund.lower() else None))
    finish(out, "greatnorth", ("company_url", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
