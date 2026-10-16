#!/usr/bin/env python3
"""Z Venture Capital (ZVC) portfolio scraper -> zvc_companies.json
Source: https://zvc.vc/portfolio/ — WordPress list `li.styles_portfolioContent`:
company name (as published, some in Japanese), hashtag tags (region,
sector, fund e.g. #Japan #AI #ZVC2) and website URL. Region tags and fund
tags are split out; the remaining tags are kept as published sectors.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://zvc.vc/portfolio/"
PRIMARY = "Z Venture Capital"
REGIONS = {"Japan", "US", "Asia", "Korea", "Europe", "India", "Global"}
FUND_TAG = re.compile(r"(ZVC|YJ)\d*|LVG|LVJ")  # ZVC / YJ Capital / LINE Ventures fund tags
SKIP = {"Other", "Others", "Area", "Sector"}  # taxonomy headers, not sectors
SECTOR_MAP = {"media": ["Gaming / Media / Entertainment"], "fintech": ["FinTech / Insurance"],
              "healthcare": ["Health"], "crypto": ["Web3 / Crypto"], "cybersecurity": ["Cybersecurity"],
              "data": ["Data & Analytics"], "hr": ["Future of Work"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select("li[class*='portfolioContent']"):
        h = it.select_one("h3")
        if not h or not clean(h.get_text()):
            continue
        tags = [clean(t.get_text(strip=True)).lstrip("#") for t in it.select("p[class*='portfolioTag']")]
        funds = [t for t in tags if FUND_TAG.fullmatch(t)]
        regions = [t for t in tags if t in REGIONS]
        secs = [t for t in tags if t not in funds and t not in regions and t not in SKIP]
        a = it.select_one("a[href]")
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        out.append(rec(h.get_text(" ", strip=True), None, href, PRIMARY, SOURCE_URL, scraped_at, sectors=secs, sector_map=SECTOR_MAP,
                       region=", ".join(regions) or None, fund=", ".join(funds) or None))
    finish(out, "zvc", ("company_url", "region", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
