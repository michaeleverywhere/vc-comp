#!/usr/bin/env python3
"""Main Sequence portfolio scraper -> mainsequence_companies.json
Source: https://www.mseq.vc/all-companies — Webflow CMS `.company-card`
items: company name, one-line description and a Main Sequence company page
(/msv-company-page/<slug>).
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.mseq.vc/all-companies"
PRIMARY = "Main Sequence"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for c in soup.select(".company-card"):
        nm = c.select_one(".names")
        if not nm or not clean(nm.get_text()):
            continue
        d = c.select_one(".description-text")
        a = c.select_one("a[href]")
        out.append(rec(nm.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None, None,
                       PRIMARY, SOURCE_URL, scraped_at, detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "mainsequence", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
