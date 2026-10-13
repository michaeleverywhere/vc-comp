#!/usr/bin/env python3
"""Joyance Partners portfolio scraper -> joyance_companies.json
Source: https://www.joyancepartners.com/portfolio — Webflow cards
(.heading-5 name + .paragraph-2 description; duplicates from responsive layout).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, prune_substring_tags, apply_tag_overrides, webflow_pages)
from _d20_common import write_out

SOURCE_URL = "https://www.joyancepartners.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "joyance_companies.json")
PRIMARY = "Joyance Partners"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for h in soup.select(".heading-5"):
            name = clean(h.get_text(" "))
            if not name or name.lower() in seen or name.isdigit() or name.lower() in ("all", "year", "fund", "category"):
                continue
            # description: next paragraph-2 siblings/neighbors
            desc = None
            for p in h.find_all_next(class_="paragraph-2", limit=6):
                t = clean(p.get_text(" "))
                if t and len(t) > 25:
                    desc = t
                    break
            seen.add(name.lower())
            out.append({
                "company_name": name,
                "description": desc,
                "company_url": None,
                "sectors": [],
                "everywhere_tags": tags_for(name, desc),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
