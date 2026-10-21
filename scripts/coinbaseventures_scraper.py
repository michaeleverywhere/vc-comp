#!/usr/bin/env python3
"""Coinbase Ventures portfolio scraper -> coinbaseventures_companies.json
Source: https://www.coinbase.com/ventures/portfolio — portfolio gallery rendered client-side (read via
headless Chrome): one card per company in the "ventures-portfolio-gallery" grid — company name (card
heading), Coinbase Ventures' one-line description where published, website where linked, and the
card's "Acquired" badge where shown."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.coinbase.com/ventures/portfolio"
PRIMARY = "Coinbase Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 20000, min_len=200000), "html.parser")
    out = []
    for grid in s.select('[data-testid^="ventures-portfolio-gallery-grid"]'):
        for card in grid.select('[data-testid="card-basic"]'):
            h = card.select_one("h3")
            name = clean(h.get_text(" ", strip=True)) if h else None
            if not name:
                continue
            ps = [clean(p.get_text(" ", strip=True)) for p in card.select("p")]
            ps = [p for p in ps if p and p != name and p.lower() != "acquired"]
            web = None
            for a in card.select("a[href^=http]"):
                href = a["href"].strip()
                if "coinbase.com" not in href and not is_social(href):
                    web = href
                    break
            acquired = any(clean(x.get_text(" ", strip=True)) == "Acquired" for x in card.select("span, div") if not x.find(["span", "div"]))
            out.append(rec(name, ps[0] if ps else None, web, PRIMARY, SOURCE_URL, scraped_at,
                           status="acquired" if acquired else None))
    if len(out) < 300:
        raise SystemExit(f"FATAL: only {len(out)} Coinbase Ventures companies")
    finish(out, "coinbaseventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
