#!/usr/bin/env python3
"""Breakout Ventures portfolio scraper -> breakout_companies.json
Source: https://breakout.vc/portfolio — Next.js/Prismic page; `li` company
entries with name (published in capitals, kept as published), one-line
description and website link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://breakout.vc/portfolio"
PRIMARY = "Breakout Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for li in soup.select("li[class*='company_entry']"):
        nm = li.select_one("[class*='company_entryName']")
        if not nm or not clean(nm.get_text()):
            continue
        d = li.select_one("[class*='company_entryDescription']")
        a = li.select_one("a[href]")
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        out.append(rec(nm.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None, href,
                       PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "breakout", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
