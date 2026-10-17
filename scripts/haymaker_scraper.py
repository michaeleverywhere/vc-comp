#!/usr/bin/env python3
"""Haymaker Ventures portfolio scraper -> haymaker_companies.json
Source: https://www.haymaker.com/portfolio — portfolio page: current Portfolio and Previous
Investments grids of company names linking to their websites."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.haymaker.com/portfolio"
PRIMARY = "Haymaker Ventures"


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
    for g in s.select(".w-layout-grid"):
        h = g.find_previous(["h1", "h2", "h3"])
        head = txt(h) or ""
        if head not in ("Portfolio", "Previous Investments"):
            continue
        for a in g.select("a[href]"):
            nm = txt(a)
            if nm:
                out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at,
                               portfolio_status="current" if head == "Portfolio" else "previous"))
    finish(out, "haymaker", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
