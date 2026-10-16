#!/usr/bin/env python3
"""Cervin Ventures portfolio scraper -> cervin_companies.json
Source: https://www.cervinventures.com/portfolio — server-rendered (HubSpot)
cards: company name (h2), stages invested (.portfolio-tags) and one-line
description (.post-content); each links to a Cervin detail page.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.cervinventures.com/portfolio"
PRIMARY = "Cervin Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select("a[href]"):
        nm = a.select_one(".portfolio-name h2")
        if not nm:
            continue
        tg = a.select_one(".portfolio-tags")
        stages = [clean(x) for x in tg.get_text("|", strip=True).split("|") if clean(x) and clean(x) != "/"] if tg else []
        d = a.select_one(".post-content")
        out.append(rec(nm.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None, None,
                       PRIMARY, SOURCE_URL, scraped_at, stages_invested=stages or None, detail_url=a["href"]))
    finish(out, "cervin", ("description", "stages_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
