#!/usr/bin/env python3
"""Ecliptic Capital portfolio scraper -> eclipticcapital_companies.json
Source: https://www.eclipticcapital.com/portfolio — Ecliptic Capital (San Francisco), early-stage venture firm backing
technology, life-science and consumer companies. The client-rendered (React/Contentful) portfolio page shows one card
per company with its name, sector, one-line description and a "Visit website" link; the page is rendered with headless
Chrome before parsing."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urlparse, unquote, urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.eclipticcapital.com/portfolio"
PRIMARY = "Ecliptic Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=3000), "html.parser")
    out = []
    for a in s.find_all("a", href=True):
        if (clean(a.get_text(" ", strip=True)) or "").upper() != "VISIT WEBSITE":
            continue
        card = a.parent.parent if a.parent else None
        spans = [clean(x.get_text(" ", strip=True)) for x in card.find_all("span", recursive=False)] if card else []
        if len(spans) < 1 or not spans[0]:
            continue
        out.append(rec(spans[0], spans[2] if len(spans) > 2 else None, a["href"], PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[spans[1]] if len(spans) > 1 and spans[1] else []))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Ecliptic Capital companies")
    finish(out, "eclipticcapital", ("description", "company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
