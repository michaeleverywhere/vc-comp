#!/usr/bin/env python3
"""HOF Capital portfolio scraper -> hofcapital_companies.json
Source: https://hofcapital.com/portfolio/ — Gatsby page-data JSON behind the
page (portfolioitems: title, companylink, sectors, published). "Publicly Listed"
sector label -> status ipo. Site publishes no descriptions.
"""
import json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch
from _d50_common import rec, finish

SOURCE_URL = "https://hofcapital.com/portfolio/"
DATA_URL = "https://hofcapital.com/page-data/portfolio/page-data.json"
PRIMARY = "HOF Capital"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "consumer": ["Consumer"], "biotech": ["BioTech", "Health"],
              "frontier": ["Deeptech / Robotics / AR/VR"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    d = json.loads(fetch(DATA_URL))
    out = []
    for it in d["result"]["data"]["companies"]["frontmatter"]["portfolioitems"]:
        if not it.get("published"):
            continue
        secs = it.get("sectors") or []
        out.append(rec(it.get("title"), None, it.get("companylink"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[s for s in secs if s != "Publicly Listed"], sector_map=SECTOR_MAP,
                       status="ipo" if "Publicly Listed" in secs else None))
    finish(out, "hofcapital", ("company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
