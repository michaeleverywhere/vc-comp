#!/usr/bin/env python3
"""Fuel Capital portfolio scraper -> fuelcapital_companies.json
Source: https://www.fuelcapital.com/portfolio — Squarespace image slides
(name from img alt, website from anchor).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.fuelcapital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "fuelcapital_companies.json")
PRIMARY = "Fuel Capital"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a.image-slide-anchor[href]"):
        img = a.find("img")
        name = clean(img.get("alt") if img else None)
        if not name or name.lower() in seen:
            continue
        if re.search(r"\.(png|jpg|svg|webp)$", name, re.I) or "_" in name and name.lower().endswith("png"):
            # filename leaked into alt
            name = clean(re.sub(r"[-_].*$", "", name).replace("-", " "))
            if not name or len(name) < 2:
                continue
        seen.add(name.lower())
        href = a.get("href")
        url = clean_url(href) if href and href.startswith("http") and "fuelcapital.com" not in href and not is_social(href) else None
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
