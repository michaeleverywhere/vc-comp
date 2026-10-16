#!/usr/bin/env python3
"""Refactor Capital portfolio scraper -> refactor_companies.json
Source: https://refactor.com/ — Webflow CMS: `.portfolio-list-item` cards
(data-company-id, name, hidden category) and `.portfolio-info-list-item`
panels (same data-company-id: website link and a short description that
continues the name, e.g. "is bringing land back online.", kept verbatim).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://refactor.com/"
PRIMARY = "Refactor Capital"
SECTOR_MAP = {"health": ["Health"], "climate": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    info = {}
    for it in soup.select(".portfolio-info-list-item[data-company-id]"):
        a = it.select_one("a.portfolio-link[href]")
        d = it.select_one(".info-text")
        info[it["data-company-id"]] = (a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None,
                                       clean(d.get_text(" ", strip=True)) if d else None)
    out = []
    for it in soup.select(".portfolio-list-item[data-company-id]"):
        nm = it.select_one(".company-name")
        if not nm or not clean(nm.get_text()):
            continue
        site, desc = info.get(it["data-company-id"], (None, None))
        cats = [clean(c.get_text(" ", strip=True)) for c in it.select("[fs-cmsfilter-field='category']")]
        out.append(rec(nm.get_text(" ", strip=True), desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[c for c in cats if c], sector_map=SECTOR_MAP))
    finish(out, "refactor", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
