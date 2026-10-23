#!/usr/bin/env python3
"""Vectr Ventures portfolio scraper -> vectrventures_companies.json
Source: https://vectr.co/portfolio — Vectr Ventures, Hong Kong / New York early-stage venture firm; the rendered
Gatsby portfolio grid gives each company's name, Vectr's one-line description and the company website."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, clean_url
from _chrome_dom import dom
from _d50_common import rec, finish

SOURCE_URL = "https://vectr.co/portfolio"
PRIMARY = "Vectr Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(dom(SOURCE_URL, 15000, tries=3, min_len=100000), "html.parser")
    out = []
    for card in soup.select('div[class*="index-module--project--"]'):
        n = card.select_one('div[class*="index-module--name--"] span') or card.select_one('div[class*="index-module--name--"]')
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name:
            continue
        top = card.select_one('div[class*="index-module--hiddenTop--"]')
        a = card.select_one("a[href]")
        out.append(rec(name, clean(top.get_text(" ", strip=True)) if top else None,
                       clean_url(a["href"]) if a else None, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 70:
        raise SystemExit(f"FATAL: only {len(out)} Vectr companies")
    finish(out, "vectrventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
