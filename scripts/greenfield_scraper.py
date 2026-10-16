#!/usr/bin/env python3
"""Greenfield Capital (Greenfield One) portfolio scraper -> greenfield_companies.json
Source: https://greenfieldcapital.com/portfolio/ — WordPress (Avada) gallery: each
item's rollover title gives the project name and its website link. No descriptions.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://greenfieldcapital.com/portfolio/"
PRIMARY = "Greenfield Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch_response(SOURCE_URL).content, "html.parser")
    out = []
    for a in soup.select("h4.fusion-rollover-title a.fusion-rollover-title-link"):
        name = clean(a.get_text(" ", strip=True))
        href = (a.get("href") or "").strip()
        if not name:
            continue
        out.append(rec(name, None, href if href.startswith("http") and "greenfieldcapital" not in href else None,
                       PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "greenfield", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
