#!/usr/bin/env python3
"""Spring Camp portfolio scraper -> springcamp_companies.json
Source: https://www.springcamp.co/portfolio — server-rendered (Angular SSR)
`a.company-card` list: company name, category and website link. No
descriptions are published on the list.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.springcamp.co/portfolio"
PRIMARY = "Spring Camp"
SECTOR_MAP = {"consumer": ["Consumer"], "fintech": ["FinTech / Insurance"], "healthcare": ["Health"], "ai & robotics": ["Deeptech / Robotics / AR/VR"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select("a.company-card"):
        nm = a.select_one(".card-name")
        if not nm:
            continue
        cat = a.select_one(".card-category")
        href = a.get("href") or ""
        out.append(rec(nm.get_text(" ", strip=True), None, href if href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[clean(cat.get_text(" ", strip=True))] if cat else [],
                       sector_map=SECTOR_MAP))
    finish(out, "springcamp", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
