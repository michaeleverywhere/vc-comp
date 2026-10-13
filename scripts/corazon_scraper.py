#!/usr/bin/env python3
"""Corazon Capital portfolio scraper -> corazon_companies.json
Source: https://www.corazon.com/portfolio — Wix repeater; company websites on
"Go" links; names derived from domain (logos lack useful alts).
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.corazon.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "corazon_companies.json")
PRIMARY = "Corazon Capital"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def name_from_url(url):
    host = urlsplit(url).netloc.lower().removeprefix("www.")
    # common multi-level: home.foodsby.com -> foodsby
    parts = host.split(".")
    if len(parts) >= 3 and parts[0] in ("home", "app", "www", "get", "landing", "go"):
        base = parts[1]
    else:
        base = parts[0]
    return clean(base.replace("-", " ").title())


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select(".wixui-repeater__item a[href^=http]"):
        href = a["href"]
        if "wix" in href or "corazon.com" in href or is_social(href):
            continue
        url = clean_url(href)
        if not url:
            continue
        name = name_from_url(url)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
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
