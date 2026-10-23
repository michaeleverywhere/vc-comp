#!/usr/bin/env python3
"""Nysnø Klimainvesteringer portfolio scraper -> nysno_companies.json
Source: https://nysnoinvest.no/en/portfolio/ — Nysnø, Norway's state-owned climate venture investor. Each portfolio
card (a.portfolio__item) gives the company name, Nysnø's one-line description, a case-type (active companies /
realized investments / fund) and a case-page link. Fund commitments (case type "fund") are not companies and are
skipped."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://nysnoinvest.no/en/portfolio/"
PRIMARY = "Nysnø"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select("a.portfolio__item"):
        types = (a.get("data-case-types") or "").split()
        if "fund" in types or "funds" in types:
            continue
        h = a.select_one("h3")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        p = a.select_one("p")
        status = "exited" if any("realized" in t for t in types) else ("active" if types else None)
        out.append(rec(name, clean(p.get_text(" ", strip=True)) if p else None, None, PRIMARY, SOURCE_URL,
                       scraped_at, status=status, profile_url=a.get("href")))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Nysnø companies")
    finish(out, "nysno", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
