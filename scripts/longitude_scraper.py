#!/usr/bin/env python3
"""Longitude Capital portfolio scraper -> longitude_companies.json
Source: https://www.longitudecapital.com/ — homepage portfolio tiles
(.community-logo): name, description, status (current/exited), sector class,
website.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.longitudecapital.com/"
PRIMARY = "Longitude Capital"
SECTOR_MAP = {"biopharmaceuticals": ["BioTech", "Health"], "biopharmaceutical": ["BioTech", "Health"],
              "medical technology": ["Health"], "medical devices": ["Health"], "healthcare services": ["Health"],
              "healthcare technology": ["Health"], "health tech": ["Health"], "life science tools": ["BioTech"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for c in soup.select(".community-logo"):
        nm = c.select_one(".company-name")
        if not nm:
            continue
        cls = [x for x in c.get("class", []) if x not in ("community-logo",)]
        st_el = c.select_one(".status-cell")
        st = clean(st_el.get_text(" ", strip=True).replace("Status:", "")) if st_el else None
        sectors = [x.replace("-", " ") for x in cls if x not in ("exited", "current", "active")]
        a = c.select_one(".company-link a[href]")
        ab = c.select_one(".company-about")
        status = {"exited": "exited", "current": "active", "active": "active"}.get((st or "").lower(), st)
        out.append(rec(nm.get_text(" ", strip=True), ab.get_text(" ", strip=True) if ab else None, a["href"] if a else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP, status=status))
    finish(out, "longitude", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
