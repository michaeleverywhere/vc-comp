#!/usr/bin/env python3
"""Ludlow Ventures portfolio scraper -> ludlow_companies.json
Source: https://ludlowventures.com/ — homepage .logo-item grid (names from img alt).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://ludlowventures.com/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "ludlow_companies.json")
PRIMARY = "Ludlow Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".logo-item"):
        img = it.select_one("img[alt]")
        raw = clean(img.get("alt") if img else None)
        if not raw:
            continue
        name = re.sub(r"(?i)\s*logo$", "", raw).strip()
        name = clean(name)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        a = it.select_one("a[href^=http]")
        url = clean_url(a["href"]) if a and "ludlowventures.com" not in a["href"] and not is_social(a["href"]) else None
        out.append({
            "company_name": name,
            "description": None,
            "company_url": url,
            "everywhere_tags": tags_for(name, None),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
