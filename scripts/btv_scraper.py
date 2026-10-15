#!/usr/bin/env python3
"""Better Tomorrow Ventures portfolio scraper -> btv_companies.json
Source: https://www.btv.vc/ — homepage lists portfolio company name+website links.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.btv.vc/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "btv_companies.json")
PRIMARY = "Better Tomorrow Ventures"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        name = clean(a.get_text(" "))
        if not name or name.lower() in seen:
            continue
        if not href.startswith("http"):
            continue
        if any(x in href for x in ("btv.vc", "linkedin.com", "twitter.com", "x.com", "ghost.io", "better-tomorrow")):
            continue
        if len(name) > 40 or len(name) < 2:
            continue
        # skip person-looking names (two+ capitalized tokens with no company cues) when linkedin already filtered
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
