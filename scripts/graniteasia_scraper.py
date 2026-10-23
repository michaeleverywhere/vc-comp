#!/usr/bin/env python3
"""Granite Asia portfolio scraper -> graniteasia_companies.json
Source: https://www.graniteasia.com/portfolio — Granite Asia (formerly GGV Capital's Asia team), Asia-focused
venture firm; the rendered Next.js portfolio grid gives each company's name (the card's "Visit <name>" label),
website and Granite Asia's tags: sector plus an outcome tag (IPO / Acquired) where the firm marks one."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, clean_url
from _chrome_dom import dom
from _d50_common import rec, finish

SOURCE_URL = "https://www.graniteasia.com/portfolio"
PRIMARY = "Granite Asia"
OUTCOMES = {"ipo": "ipo", "acquired": "acquired"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(dom(SOURCE_URL, 15000, tries=3, min_len=50000), "html.parser")
    out = []
    for a in soup.select('a[aria-label^="Visit "]'):
        name = clean(a["aria-label"][len("Visit "):])
        if not name:
            continue
        tags = [clean(c.get_text(" ", strip=True)) for c in a.select("div.caption")]
        tags = [t for t in tags if t]
        outcome = next((OUTCOMES[t.lower()] for t in tags if t.lower() in OUTCOMES), None)
        sectors = [t for t in tags if t.lower() not in OUTCOMES]
        out.append(rec(name, None, clean_url(a.get("href")), PRIMARY, SOURCE_URL, scraped_at, sectors=sectors,
                       status=outcome, ipo=True if outcome == "ipo" else None,
                       acquired=True if outcome == "acquired" else None))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Granite Asia companies")
    finish(out, "graniteasia", ("company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
