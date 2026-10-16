#!/usr/bin/env python3
"""Courtside Ventures portfolio scraper -> courtside_companies.json
Source: https://www.courtsidevc.com/portfolio — Webflow CMS
`.mix-investments` cards: name (h3), country, vertical, fund, series,
acquisition text and a detail page /portfolio/<slug>.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.courtsidevc.com/portfolio"
PRIMARY = "Courtside Ventures"
SECTOR_MAP = {"sports": ["Gaming / Media / Entertainment"], "gaming": ["Gaming / Media / Entertainment"],
              "media": ["Gaming / Media / Entertainment"]}


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".mix-investments"):
        nm = txt(it.select_one("h3"))
        if not nm:
            continue
        vert = txt(it.select_one(".filter-vertical"))
        acq = txt(it.select_one(".acquired-text"))
        a = it.select_one("a[href]")
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[vert] if vert else [],
                       sector_map=SECTOR_MAP, country=txt(it.select_one(".filter-country")),
                       fund=txt(it.select_one(".filter-fund")), stage=txt(it.select_one(".filter-series")),
                       exit_note=acq, status="acquired" if acq and acq.lower().startswith("acquired") else None,
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "courtside", ("country", "fund", "stage", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
