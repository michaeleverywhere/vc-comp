#!/usr/bin/env python3
"""TEN13 portfolio scraper -> ten13_companies.json
Source: https://www.ten13.vc/portfolio — Webflow CMS cards: company name
(h1), sector, description and website link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.ten13.vc/portfolio"
PRIMARY = "TEN13"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".extrapadding.w-dyn-item"):
        h = it.find("h1")
        if not h or not clean(h.get_text()):
            continue
        sec = it.select_one(".sector")
        d = it.select_one(".portfolio-desc")
        a = it.select_one("a[href]")
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        sec = clean(sec.get_text(" ", strip=True)) if sec else None
        out.append(rec(h.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None, href,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else []))
    finish(out, "ten13", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
