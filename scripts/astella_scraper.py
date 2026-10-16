#!/usr/bin/env python3
"""Astella portfolio scraper -> astella_companies.json
Source: https://www.astella.com.br/en/portfolio — Webflow CMS list of company
names (`h5.porfolio-name`) linked to company websites. No descriptions or
status are published on the list.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.astella.com.br/en/portfolio"
PRIMARY = "Astella"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        for h in BeautifulSoup(html, "html.parser").select("h5.porfolio-name"):
            a = h.find_parent("a")
            href = (a.get("href") if a else "") or ""
            out.append(rec(h.get_text(" ", strip=True), None, href if href.startswith("http") and not is_social(href) else None,
                           PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "astella", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
