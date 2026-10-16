#!/usr/bin/env python3
"""TA Associates portfolio scraper -> ta_companies.json
Source: https://www.ta.com/portfolio/ — server-rendered (Nuxt) table of every
company: Company Name, Sector, Region, Status (Current/Past). No descriptions or
websites are published.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.ta.com/portfolio/"
PRIMARY = "TA Associates"
SECTOR_MAP = {"financial services": ["FinTech / Insurance"], "healthcare": ["Health"], "consumer": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for h in soup.find_all("h3"):
        if clean(h.get_text()) != "Company Name":
            continue
        row = h.parent.parent
        f = {}
        for cell in row.find_all("div", recursive=False):
            lab, val = cell.find(["h3", "h4"]), cell.find("span")
            if lab and val:
                f[clean(lab.get_text())] = clean(val.get_text())
        name = f.get("Company Name")
        if not name:
            continue
        sectors = [s.strip() for s in (f.get("Sector") or "").split(",") if s.strip()]
        st = (f.get("Status") or "").lower()
        out.append(rec(name, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP,
                       region=f.get("Region"), portfolio_status=f.get("Status"),
                       status={"current": "active", "past": "realized"}.get(st, st or None)))
    finish(out, "ta", ("status", "region", "everywhere_tags"))


if __name__ == "__main__":
    main()
