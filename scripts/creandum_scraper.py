#!/usr/bin/env python3
"""Creandum portfolio scraper -> creandum_companies.json
Source: https://creandum.com/commitments/ — Vue/Contentful .portfolio-card
(name via logo img alt, description via .desc, exited via .exited class).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://creandum.com/commitments/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "creandum_companies.json")
PRIMARY = "Creandum"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for card in soup.select(".portfolio-card"):
        img = card.select_one(".logo img[alt], img[alt]")
        name = clean(img.get("alt") if img else None)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc_el = card.select_one(".desc")
        desc = clean(desc_el.get_text(" ")) if desc_el else None
        exited = "exited" in (card.get("class") or [])
        status = "acquired" if exited else "active"
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": None,
            "sectors": [],
            "status": status,
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
