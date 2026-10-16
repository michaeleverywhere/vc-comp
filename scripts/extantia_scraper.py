#!/usr/bin/env python3
"""Extantia Capital portfolio scraper -> extantia_companies.json
Source: https://www.extantia.com/pioneers — Webflow list (name, fund tag such as
"Flagship"; "Allstars" fund commitments skipped) plus each pioneer page: SECTOR, STAGE, COUNTRY, website.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, label_after, is_social
from _d50_common import rec, finish, page_strings

SOURCE_URL = "https://www.extantia.com/pioneers"
PRIMARY = "Extantia Capital"
LABELS = {"sector", "stage", "category", "country", "website"}


def val(st, label):
    v = label_after(st, label)
    return None if (v is None or v.lower() in LABELS or v.startswith("<svg")) else v


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    items = {}
    for it in soup.select(".w-dyn-item"):
        a = it.select_one("a[href^='/pioneers/']")
        strs = [clean(x) for x in it.stripped_strings if clean(x) and clean(x) != "Read"]
        if a and strs:
            link = urljoin(SOURCE_URL, a["href"])
            items.setdefault(link, strs)
    pages = fetch_many(list(items), workers=6, pause=0.1)
    out = []
    for link, strs in items.items():
        name = strs[0]
        fund = strs[1] if len(strs) > 1 else None
        if fund == "Allstars":  # fund-of-funds commitments (other VC funds), not portfolio companies
            continue
        st, s = page_strings(pages.get(link) or "")
        st = [x for x in st if not x.startswith("<svg")]
        site = None
        for a in (s.select("a[href^=http]") if pages.get(link) else []):
            h = a["href"]
            if "extantia" not in h and not is_social(h) and "fundrbird" not in h and "breezy" not in h and "join.com" not in h:
                site = h; break
        sector = val(st, "SECTOR")
        out.append(rec(name, None, site, PRIMARY, SOURCE_URL, scraped_at, sectors=[sector] if sector else [],
                       sector_map={(sector or "").lower(): ["Climate / Sustainability"]},
                       stage=val(st, "STAGE"), location=val(st, "COUNTRY"), category=val(st, "CATEGORY"), fund=fund,
                       detail_url=link))
    finish(out, "extantia", ("company_url", "stage", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
