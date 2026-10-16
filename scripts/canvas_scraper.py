#!/usr/bin/env python3
"""Canvas Ventures portfolio scraper -> canvas_companies.json
Source: https://canvas.vc/portfolio — Webflow CMS cards (`.co-item`): company
name, one-line description, sector label, website link and exit/ticker note
(e.g. "Acquired by Allscripts (MDRX)").
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://canvas.vc/portfolio"
PRIMARY = "Canvas Ventures"
SECTOR_MAP = {"digital health": ["Health"], "fintech": ["FinTech / Insurance"], "consumer": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".co-item.w-dyn-item"):
            nm = it.select_one(".card-name")
            if not nm:
                continue
            a = it.select_one("a[href^=http]")
            rel = it.select_one("a[href^='/companies/']")
            lab = [clean(l.get_text(" ", strip=True)) for l in it.select(".label-text")]
            tick = it.select_one(".ticker-text")
            note = clean(tick.get_text(" ", strip=True)) if tick and "w-dyn-bind-empty" not in (tick.get("class") or []) else None
            nl = (note or "").lower()
            out.append(rec(nm.get_text(" ", strip=True), it.select_one(".card-title") and it.select_one(".card-title").get_text(" ", strip=True),
                           a["href"] if a and not is_social(a["href"]) else None, PRIMARY, SOURCE_URL, scraped_at,
                           sectors=[l for l in lab if l], sector_map=SECTOR_MAP, exit_note=note,
                           detail_url="https://canvas.vc" + rel["href"] if rel else None,
                           status="acquired" if "acquired" in nl else "ipo" if ("nyse" in nl or "nasdaq" in nl or "ipo" in nl) else None))
    finish(out, "canvas", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
