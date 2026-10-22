#!/usr/bin/env python3
"""Quiet Capital portfolio scraper -> quietcapital_companies.json
Source: https://quiet.com/portfolio/ — San Francisco venture firm; WordPress site whose portfolio page is fed by the
public WP REST post type "portfolio" (/wp-json/wp/v2/portfolio): company name, the firm's own sector label(s)
("portfolio-type": AI, Consumer, Crypto, Deeptech, Enterprise, Fintech, Healthcare, Marketplace) and profile link."""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text
from _d50_common import rec, finish, wp_all, wp_terms

SOURCE_URL = "https://quiet.com/portfolio/"
ORIGIN = "https://quiet.com"
PRIMARY = "Quiet Capital"
SECTOR_MAP = {"crypto": ["Web3 / Crypto"], "fintech": ["FinTech / Insurance"], "healthcare": ["Health"],
              "consumer": ["Consumer"], "deeptech": ["Deeptech / Robotics / AR/VR"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    types = wp_terms(ORIGIN, "portfolio-type")
    out = []
    for p in wp_all(ORIGIN, "portfolio"):
        name = html_text(p["title"]["rendered"])
        if not name:
            continue
        sectors = [types[t] for t in p.get("portfolio-type") or [] if t in types]
        desc = html_text(p.get("content", {}).get("rendered") or "") or html_text(p.get("excerpt", {}).get("rendered") or "")
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP,
                       profile_url=p.get("link")))
    if len(out) < 150:
        raise SystemExit(f"FATAL: only {len(out)} Quiet Capital companies")
    finish(out, "quietcapital", ("description", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
