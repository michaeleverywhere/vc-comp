#!/usr/bin/env python3
"""Fogline VC portfolio scraper -> foglinevc_companies.json
Source: https://www.fogline.vc/ — the portfolio grid on the home page (JS-rendered, read via
headless Chrome): company name, Fogline's one-word category (Dev Tools / Cybersecurity / Deep
Tech …) and the company website (card link)."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.fogline.vc/"
PRIMARY = "Fogline VC"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 12000, min_len=20000), "html.parser")
    out = []
    for a in s.select("a.cell"):
        n = a.select_one(".co-name")
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name:
            continue
        m = a.select_one(".co-meta")
        sector = clean(m.get_text(" ", strip=True)) if m else None
        url = a.get("href")
        if url and (is_social(url) or not url.startswith("http")):
            url = None
        out.append(rec(name, None, url, PRIMARY, SOURCE_URL, scraped_at, sectors=[sector] if sector else None))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Fogline companies")
    finish(out, "foglinevc", ("company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
