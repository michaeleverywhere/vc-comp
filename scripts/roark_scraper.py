#!/usr/bin/env python3
"""Roark Capital portfolio scraper -> roark_companies.json
Source: https://www.roarkcapital.com/portfolio — server-rendered grid of
`article.portfolio-section__portfolio` cards whose <dialog> holds the company
name, Roark's description, website link and "Market Sectors" categories.
The page does not publish current/realized status.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.roarkcapital.com/portfolio"
PRIMARY = "Roark Capital"
SECTOR_MAP = {"franchise/multi-unit": ["Consumer"], "restaurant & food": ["Consumer"],
              "health, wellness & fitness": ["Health"], "business & consumer services": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for art in soup.select("article.portfolio-section__portfolio"):
        t = art.select_one(".portfolio-section__dialog-title")
        name = t.get_text(" ", strip=True) if t else (art.find("img") or {}).get("alt")
        content = art.select_one(".portfolio-section__dialog-content")
        desc = " ".join(p.get_text(" ", strip=True) for p in content.find_all("p")) if content else None
        a = art.select_one("a.portfolio-section__dialog-link[href^=http]")
        site = a["href"] if a and not is_social(a["href"]) else None
        cats = [c.get_text(" ", strip=True) for c in art.select(".category")]
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=cats, sector_map=SECTOR_MAP))
    finish(out, "roark", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
