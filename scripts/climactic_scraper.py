#!/usr/bin/env python3
"""Climactic portfolio scraper -> climactic_companies.json
Source: https://www.climactic.vc/portfolio — Climactic, early-stage climate-tech venture capital firm. The Webflow
portfolio collection (div.portfolio_collection-item) gives each company's name, founders with titles, Climactic's
description and website link. The page renders the collection twice (desktop / mobile); duplicates collapse by name."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.climactic.vc/portfolio"
PRIMARY = "Climactic"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select("div.portfolio_collection-item"):
        n = it.select_one(".portfolio-card_text-1")
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name:
            continue
        d = it.select_one(".portfolio-card_text-3")
        a = it.select_one("a.portfolio-card_link-text[href]")
        founders = [clean(p.get_text(" ", strip=True)) for p in it.select(".portfolio-card_rich-text p")]
        founders = [f for f in founders if f]
        out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None, a["href"] if a else None,
                       PRIMARY, SOURCE_URL, scraped_at, founders="; ".join(founders) or None))
    if len(out) < 12:
        raise SystemExit(f"FATAL: only {len(out)} Climactic companies")
    finish(out, "climactic", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
