#!/usr/bin/env python3
"""COMETA portfolio scraper -> cometa_companies.json
Source: https://www.cometa.vc/portfolio — Webflow CMS `.partners_card-item`
cards with Finsweet filter fields: business model, geography, type (sector)
and stage. Detail pages at /partners/<slug>.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.cometa.vc/portfolio"
PRIMARY = "COMETA"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".partners_card-item"):
        nm = it.select_one(".partners_card .text-size-medium")
        if not nm:
            continue
        f = {}
        for t in it.select("[fs-cmsfilter-field]"):
            f.setdefault(t["fs-cmsfilter-field"].lower(), []).append(clean(t.get_text(" ", strip=True)))
        a = it.select_one("a[href]")
        out.append(rec(nm.get_text(" ", strip=True), None, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x for x in f.get("type", []) if x],
                       business_model=", ".join(x for x in f.get("business model", []) if x) or None,
                       geography=", ".join(x for x in f.get("geography", []) if x) or None,
                       stage=", ".join(x for x in f.get("stages", []) if x) or None,
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "cometa", ("stage", "geography", "everywhere_tags"))


if __name__ == "__main__":
    main()
