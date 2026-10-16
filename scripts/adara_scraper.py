#!/usr/bin/env python3
"""Adara Ventures portfolio scraper -> adara_companies.json
Source: https://www.adara.vc/portfolios — Webflow CMS cards
(`.filter-list__item.small`): company name, tagline, status (data-filter-status:
active / exited ...), industry and detail link.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.adara.vc/portfolios"
PRIMARY = "Adara Ventures"
SECTOR_MAP = {"cybersecurity": ["Cybersecurity"], "new data frontiers": ["Data & Analytics"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".filter-list__item.small.w-dyn-item"):
            nm = it.select_one(".porfoli-thumnail-name")
            if not nm:
                continue
            tag = it.select_one(".p-body")
            ind = it.select_one(".demo-card__h3.industry")
            stg = it.select_one(".demo-card__h3.stage")
            st = clean(stg.get_text(" ", strip=True)) if stg else None
            a = it.select_one("a[href]")
            out.append(rec(nm.get_text(" ", strip=True), tag.get_text(" ", strip=True) if tag else None, None, PRIMARY,
                           SOURCE_URL, scraped_at, sectors=[clean(ind.get_text(" ", strip=True))] if ind else [],
                           sector_map=SECTOR_MAP, portfolio_status=st,
                           status={"active": "active", "exited": "exited", "we tried": "closed"}.get((st or "").lower()),
                           detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "adara", ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
