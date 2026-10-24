#!/usr/bin/env python3
"""Praetura Ventures portfolio scraper -> praeturaventures_companies.json
Source: https://www.praeturaventures.com/portfolio — Praetura Ventures, Manchester-based EIS venture investor (now
part of PXN Investments after merging with Par Equity). Each portfolio overlay gives the company name, founded year,
headquarters, sector, an "About" description and Praetura's "Why we backed" note."""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.praeturaventures.com/portfolio"
PRIMARY = "Praetura Ventures"


def field(item, label):
    for d in item.select("div.d-inline-flex"):
        t = clean(d.get_text(" "))
        if t and label + ":" in t:
            b = d.select_one(".fw-bold")
            return clean(b.get_text(" ")) if b else None
    return None


def section(item, prefix):
    h = item.find("h4", string=lambda s: s and clean(s).startswith(prefix))
    if not h:
        return None
    p = h.find_next("p")
    return clean(p.get_text(" ")) if p else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for item in soup.select(".js-overlay-item-data"):
        h1 = item.find("h1")
        name = clean(h1.get_text(" ")) if h1 else None
        if not name:
            continue
        sector = field(item, "Sector")
        out.append(rec(name, section(item, "About"), None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sector] if sector else None, founded=field(item, "Founded"),
                       headquarters=field(item, "Headquarters"), why_backed=section(item, "Why we")))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Praetura companies")
    finish(out, "praeturaventures", ("description", "founded", "headquarters", "everywhere_tags"))


if __name__ == "__main__":
    main()
