#!/usr/bin/env python3
"""Fly Ventures portfolio scraper -> flyventures_companies.json
Source: https://www.fly.vc/portfolio — SSR company name links to company sites
(plus founder LinkedIn links which are ignored).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.fly.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "flyventures_companies.json")
PRIMARY = "Fly Ventures"
SKIP = {"portfolio", "team", "how we invest", "imprint", "privacy", "sfdr", "all categories",
        "ai", "dev tools & infrastructure", "industrial automation", "techbio"}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        name = clean(a.get_text(" "))
        if not name or name.lower() in SKIP or name.lower() in seen:
            continue
        if not href.startswith("http"):
            continue
        if "fly.vc" in href or "linkedin.com" in href or "twitter.com" in href:
            continue
        # company site link with short name
        if len(name) > 40:
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": None,
            "company_url": clean_url(href),
            "sectors": [],
            "everywhere_tags": tags_for(name, None),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
