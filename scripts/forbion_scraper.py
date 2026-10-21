#!/usr/bin/env python3
"""Forbion portfolio scraper -> forbion_companies.json
Source: https://forbion.com/en/portfolio/ — life-sciences portfolio grid rendered client-side (read via
headless Chrome, pressing the page's own "Show more" button until all cards are shown): one card per
company — company name, Forbion's one-line description, therapeutic-area label and the Forbion company page."""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_jsclick import dom_jsclick

SOURCE_URL = "https://forbion.com/en/portfolio/"
PRIMARY = "Forbion"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = dom_jsclick(SOURCE_URL, "[...document.querySelectorAll('button')].find(b => /^\\s*show more\\s*$/i.test(b.innerText) && b.offsetParent !== null)",
                       "document.querySelectorAll('a.page-url').length", step_s=2)
    s = BeautifulSoup(html, "html.parser")
    out = []
    for a in s.select("a.page-url"):
        h = a.select_one(".card-content h6")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        d = a.select_one(".card-content .body-small")
        area = a.select_one(".card-bottom .body-small")
        area = clean(area.get_text(" ", strip=True)) if area else None
        out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[area] if area else [], profile_url=urljoin(SOURCE_URL, a.get("href") or "")))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Forbion companies")
    finish(out, "forbion", ("description", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
