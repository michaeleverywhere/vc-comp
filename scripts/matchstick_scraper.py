#!/usr/bin/env python3
"""Matchstick Ventures portfolio scraper -> matchstick_companies.json
Source: https://www.matchstick.vc/companies — Webflow CMS overview cards
(`.collection-item` with an /companies/<slug> link): company name, one-line
description and detail page. Logo-grid items (no text) are ignored.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.matchstick.vc/companies"
PRIMARY = "Matchstick Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".collection-item.w-dyn-item"):
        a = it.select_one("a[href^='/companies/']")
        strs = [clean(s) for s in it.stripped_strings if clean(s)]
        if not a or len(strs) < 2:
            continue
        name, desc = strs[0], strs[1] if strs[1] != "Read overview" else None
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, detail_url=urljoin(SOURCE_URL, a["href"])))
    finish(out, "matchstick", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
