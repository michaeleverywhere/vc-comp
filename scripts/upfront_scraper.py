#!/usr/bin/env python3
"""Upfront Ventures portfolio scraper -> upfront_companies.json
Source: https://upfront.com/portfolio — Angular app (content rendered client-side),
read from the rendered DOM via headless Chrome (_chrome_dom.py): each accordion row
gives company name, one-line description, status badge (Acquired / IPO / blank =
active), CEO, location and website."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, is_social
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://upfront.com/portfolio"
PRIMARY = "Upfront Ventures"
STATUS = {"": "active", "acquired": "acquired", "ipo": "ipo"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=200000), "html.parser")
    out = []
    for p in s.select("mat-expansion-panel"):
        t = p.select_one(".title")
        name = clean(t.get_text(" ", strip=True)) if t else None
        if not name:
            continue
        desc = p.select_one(".description")
        badge = (clean(p.select_one(".status").get_text(" ", strip=True)) or "") if p.select_one(".status") else ""
        info = {}
        for blk in p.select(".info > div"):
            lab, val = blk.select_one(".label"), blk.select_one(".value")
            if lab and val:
                info[(clean(lab.get_text(" ", strip=True)) or "").lower()] = val
        web = info.get("website")
        a = web.select_one("a[href]") if web else None
        href = a["href"].strip() if a else None
        ceo = clean(info["ceo"].get_text(" ", strip=True)) if "ceo" in info else None
        loc = clean(info["location"].get_text(" ", strip=True)) if "location" in info else None
        out.append(rec(name, desc.get_text(" ", strip=True) if desc else None,
                       href if href and href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at, ceo=ceo, location=loc, exit_status=badge or None,
                       status=STATUS.get(badge.lower(), badge.lower() or "active")))
    if len(out) < 100:
        raise SystemExit(f"FATAL: only {len(out)} Upfront rows rendered (expected ~160+)")
    finish(out, "upfront", ("description", "company_url", "ceo", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
