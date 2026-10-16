#!/usr/bin/env python3
"""Multicoin Capital portfolio scraper -> multicoin_companies.json
Source: Gatsby page-data at /page-data/portfolio/page-data.json (Contentful projects).
"""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://multicoin.capital/portfolio"
PAGE_DATA = "https://multicoin.capital/page-data/portfolio/page-data.json"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "multicoin_companies.json")
PRIMARY = "Multicoin Capital"
SECTOR_MAP = {
    "decentralized finance": ["Web3 / Crypto", "FinTech / Insurance"],
    "infrastructure": ["Web3 / Crypto", "Dev Tools / Cloud"],
    "nft": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
    "consumer": ["Web3 / Crypto", "Consumer"],
    "web3": ["Web3 / Crypto"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    data = fetch(PAGE_DATA, as_json=True)
    body = (((data.get("result") or {}).get("data") or {}).get("page") or {}).get("body") or []
    projects = []
    for block in body:
        projects.extend(block.get("projects") or [])
    out, seen = [], set()
    for p in projects:
        name = clean(p.get("name") or p.get("title"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(p.get("shortDescription") or p.get("description"))
        wl = p.get("websiteLink") or {}
        website = clean_url(wl.get("url")) if isinstance(wl, dict) else None
        cats = p.get("projectCategory") or []
        if isinstance(cats, str):
            cats = [cats]
        sectors = list(cats)
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
