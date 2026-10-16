#!/usr/bin/env python3
"""Symbolic Capital portfolio scraper -> symbolic_companies.json
Source: https://www.symbolic.capital/portfolio — Webflow CMS
`.portfolio_list-item` cards: company name and website. Names and websites only.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.symbolic.capital/portfolio"
PRIMARY = "Symbolic Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    pages = webflow_pages(SOURCE_URL)
    pages = list(pages.values()) if isinstance(pages, dict) else pages
    out = []
    for html in pages:
        soup = BeautifulSoup(html, "html.parser")
        for e in soup.select(".w-condition-invisible"):
            e.decompose()
        for it in soup.select(".portfolio_list-item"):
            h = it.select_one(".portfolio_card-wrapper [class*='heading']")
            if not h or not clean(h.get_text()):
                continue
            a = it.select_one("a.box-link[href]")
            href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
            out.append(rec(h.get_text(" ", strip=True), None, href, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "symbolic", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
