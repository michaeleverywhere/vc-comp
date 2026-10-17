#!/usr/bin/env python3
"""Brainstorm Ventures portfolio scraper -> brainstormvc_companies.json
Source: https://brainstorm.vc/portfolio/ — portfolio grid
(`div.brve-filter-item`): company name, one-line description, fund (from the
filter class) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://brainstorm.vc/portfolio/"
PRIMARY = "Brainstorm Ventures"


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
    for it in s.select("div.brve-filter-item"):
        nm = txt(it.select_one(".brve-portfolio-item-title"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        fund = next((c[len("brve-filter-fund-"):] for c in it.get("class", []) if c.startswith("brve-filter-fund-")), None)
        out.append(rec(nm, txt(it.select_one(".brve-portfolio-item-content-inner")), site(it.select_one(".brve-portfolio-item-link a")),
                       PRIMARY, SOURCE_URL, scraped_at, fund=("Fund " + fund.upper()) if fund else None))
    finish(out, "brainstormvc", ("description", "company_url", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
