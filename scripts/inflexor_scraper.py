#!/usr/bin/env python3
"""Inflexor Ventures portfolio scraper -> inflexor_companies.json
Source: https://www.inflexor.vc/portfolio — Webflow CMS `.ci---portfolio`
items: name (hover chip), Finsweet filter fields Sector, Fund and Stage.
Detail pages at /portfolio/<slug>.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.inflexor.vc/portfolio"
PRIMARY = "Inflexor Ventures"
SECTOR_MAP = {"digital infrastructure": ["Dev Tools / Cloud"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".ci---portfolio"):
        nm = it.select_one(".hover-chip.name")
        if not nm:
            continue
        f = {}
        for t in it.select("[fs-cmsfilter-field]"):
            f.setdefault(t["fs-cmsfilter-field"].lower(), []).append(clean(t.get_text(" ", strip=True)))
        a = it.select_one("a[href]")
        out.append(rec(nm.get_text(" ", strip=True), None, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x for x in f.get("sector", []) if x], sector_map=SECTOR_MAP,
                       fund=", ".join(x for x in f.get("fund", []) if x) or None,
                       stage=", ".join(x for x in f.get("stage", []) if x) or None,
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "inflexor", ("stage", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
