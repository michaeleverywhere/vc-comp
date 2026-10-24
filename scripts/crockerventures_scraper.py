#!/usr/bin/env python3
"""Crocker Ventures portfolio scraper -> crockerventures_companies.json
Source: https://www.crockerventures.com/portfolio-companies-2/ — Crocker Ventures, Utah-based venture investor
(medtech/life sciences focus). The page lists "Operating Companies" and "Investment Companies"; each entry gives the
company name, location, website and a description paragraph."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url
from _d50_common import rec, finish

SOURCE_URL = "https://www.crockerventures.com/portfolio-companies-2/"
PRIMARY = "Crocker Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for h5 in soup.find_all("h5"):
        lines = [clean(x) for x in h5.get_text("\n").split("\n") if clean(x)]
        if not lines:
            continue
        grp = h5.find_previous("h2")
        group = clean(grp.get_text(" ")) if grp else None
        a = h5.find("a", href=True)
        p = h5.find_next_sibling("p")
        out.append(rec(lines[0], clean(p.get_text(" ")) if p else None, clean_url(a["href"]) if a else None,
                       PRIMARY, SOURCE_URL, scraped_at, location=lines[1] if len(lines) > 1 else None,
                       portfolio_group=group if group in ("Operating Companies", "Investment Companies") else None))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Crocker Ventures companies")
    finish(out, "crockerventures", ("description", "company_url", "location", "portfolio_group", "everywhere_tags"))


if __name__ == "__main__":
    main()
