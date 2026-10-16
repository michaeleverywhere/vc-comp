#!/usr/bin/env python3
"""Summit Partners portfolio scraper -> summit_companies.json
Source: https://www.summitpartners.com/portfolio — Webflow CMS list (paginated):
name, one-line description, sector(s), status (Current/Realized), investment date
and company page link. Websites are not given as a structured field.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, year_of
from _d50_common import rec, finish

ORIGIN = "https://www.summitpartners.com"
SOURCE_URL = ORIGIN + "/portfolio"
PRIMARY = "Summit Partners"
SECTOR_MAP = {"healthcare & life sciences": ["Health"], "healthcare": ["Health"], "financial services": ["FinTech / Insurance"],
              "consumer": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select('a[ea-nest-list="parent-trigger"]'):
            g = lambda f: [clean(x.get_text()) for x in a.select(f'[fs-cmsfilter-field="{f}"]') if clean(x.get_text())]
            name = (g("name") or [None])[0]
            if not name:
                continue
            sectors = [s for s in g("sector") if s.lower() != "sector"]
            status = (g("status") or [None])[0]
            d = a.select_one('[fs-cmssort-field="date"]')
            date = clean(d.get_text()) if d else None
            out.append(rec(name, (g("description") or [None])[0], None, PRIMARY, SOURCE_URL, scraped_at,
                           sectors=sectors, sector_map=SECTOR_MAP,
                           portfolio_status=status,
                           status={"current": "active", "realized": "realized", "merger": "acquired"}.get((status or "").lower(), (status or "").lower() or None),
                           investment_date=date or None, first_invested_year=year_of(date) if date else None,
                           detail_url=ORIGIN + a["href"] if a.get("href", "").startswith("/") else None))
    finish(out, "summit", ("description", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
