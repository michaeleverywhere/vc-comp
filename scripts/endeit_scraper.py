#!/usr/bin/env python3
"""Endeit Capital portfolio scraper -> endeit_companies.json
Source: https://www.endeit.com/portfolio — Webflow cards: name, sector tag, year,
stage (Current/Exited), website and description.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, year_of, label_after
from _d50_common import rec, finish

SOURCE_URL = "https://www.endeit.com/portfolio"
PRIMARY = "Endeit Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".collection-item"):
            card = it.select_one(".blue-card-container")
            if not card:
                continue
            nm = card.select_one(".portfoliocard .body-xl")
            if not nm:
                continue
            st = [clean(t) for t in card.select_one(".flex-h-80px").stripped_strings] if card.select_one(".flex-h-80px") else []
            sector = st[1] if len(st) > 1 and st[0] == clean(nm.get_text()) else None
            d = card.select_one(".portfoliocard .paragraph")
            a = card.select_one("a[href^=http]")
            stage = label_after(st, "stage")
            out.append(rec(nm.get_text(" ", strip=True), clean(d.get_text(" ", strip=True)) if d else None, a["href"] if a else None,
                           PRIMARY, SOURCE_URL, scraped_at, sectors=[sector] if sector and sector != "Other" else None,
                           first_invested_year=year_of(label_after(st, "year")), portfolio_status=stage,
                           status={"current": "active", "exited": "exited", "exit": "exited"}.get((stage or "").lower(), (stage or "").lower() or None)))
    finish(out, "endeit", ("description", "company_url", "first_invested_year", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
