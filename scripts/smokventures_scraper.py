#!/usr/bin/env python3
"""SMOK Ventures portfolio scraper -> smokventures_companies.json
Source: https://smok.vc/portfolio — WordPress portfolio grid (read via headless Chrome): one card per
company — company name, SMOK's hashtag labels (#AI, #legal, ...), the card's one-line description and
the SMOK company-page link."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://smok.vc/portfolio"
PRIMARY = "SMOK Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=30000), "html.parser")
    out = []
    for box in s.select("div.inner-box"):
        h = box.select_one("div.lower-content h3")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        a = h.select_one("a[href]")
        tags = [clean(b.get_text(" ", strip=True)).lstrip("#") for b in box.select("div.lower-content li button") if clean(b.get_text(" ", strip=True))]
        p = box.find("p", recursive=False)
        desc = clean(p.get_text(" ", strip=True)) if p else None
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=tags,
                       profile_url=a["href"] if a else None))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} SMOK companies")
    finish(out, "smokventures", ("description", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
