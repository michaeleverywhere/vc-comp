#!/usr/bin/env python3
"""Standard Crypto portfolio scraper -> standardcrypto_companies.json
Source: https://www.standardvc.com/portfolio/ — server-rendered (Astro) list of
`a[data-portfolio-item]` entries with data-portfolio-name (company), data-cat
(category) and website href. No descriptions are published.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.standardvc.com/portfolio/"
PRIMARY = "Standard Crypto"
SECTOR_MAP = {"fintech": ["FinTech / Insurance", "Web3 / Crypto"], "infrastructure": ["Web3 / Crypto"],
              "consumer": ["Consumer"], "gaming": ["Gaming / Media / Entertainment"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select("a[data-portfolio-item][data-portfolio-name]"):
        href = a.get("href") or ""
        cat = clean(a.get("data-cat"))
        out.append(rec(a["data-portfolio-name"], None, href if href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [], sector_map=SECTOR_MAP))
    finish(out, "standardcrypto", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
