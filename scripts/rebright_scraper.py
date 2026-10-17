#!/usr/bin/env python3
"""Rebright Partners portfolio scraper -> rebright_companies.json
Source: https://rebright.partners/portfolio/ — server-rendered WordPress portfolio grid
(portfolio_companies post type): company name, website link, sector, country and a
one-line description per card. The firm's site does not publish rounds or exit status."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://rebright.partners/portfolio/"
PRIMARY = "Rebright Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch_response(SOURCE_URL).content.decode("utf-8", "replace"), "html.parser")
    out = []
    for it in s.select(".portfolio-items-wrap .portfolio-item"):
        h = it.select_one(".titleWrap h3")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        a = it.select_one("a[href]")
        href = (a.get("href") or "") if a else ""
        sector = it.select_one(".titleWrap .meta")
        country = it.select_one(".companyMeta .meta")
        p = it.select_one(".company-info p")
        desc = clean(p.get_text(" ", strip=True)) if p else None
        sectors = [clean(sector.get_text(" ", strip=True))] if sector else []
        out.append(rec(name, desc, href if href.startswith("http") else None, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=sectors,
                       location=clean(country.get_text(" ", strip=True)) if country else None))
    finish(out, "rebright", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
