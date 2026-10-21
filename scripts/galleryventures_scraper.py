#!/usr/bin/env python3
"""Gallery Ventures (formerly Crossbeam) portfolio scraper -> galleryventures_companies.json
Source: https://gallery.vc — crossbeam.vc now redirects here; Framer site rendered client-side (read via
headless Chrome): the "Selected Portfolio" list — company names only (the site publishes no
descriptions, links or dates)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://gallery.vc"
PRIMARY = "Gallery Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 12000, min_len=50000), "html.parser")
    out = []
    head = next((h for h in s.find_all(["h2", "h3"]) if clean(h.get_text(" ", strip=True)) == "Selected Portfolio"), None)
    if head is None:
        raise SystemExit("FATAL: Selected Portfolio heading not found")
    for h in head.find_all_next("h1"):
        name = clean(h.get_text(" ", strip=True))
        if not name or re.match(r"(?i)^see all$", name):
            continue
        out.append(rec(name, None, None, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Gallery Ventures companies")
    finish(out, "galleryventures", ("everywhere_tags",))


if __name__ == "__main__":
    main()
