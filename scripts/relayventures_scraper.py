#!/usr/bin/env python3
"""Relay Ventures portfolio scraper -> relayventures_companies.json
Source: https://www.relayventures.com/portfolio/ — .team-block cards linking
to company sites (names from domain; logos lack useful alts).
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urlsplit
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.relayventures.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "relayventures_companies.json")
PRIMARY = "Relay Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def name_from_url(url):
    host = urlsplit(url).netloc.lower().removeprefix("www.")
    base = host.split(".")[0]
    return clean(base.replace("-", " ").title())


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".team-block"):
        a = it.select_one("a[href^=http]")
        if not a:
            continue
        href = a["href"]
        if "relayventures.com" in href or is_social(href):
            continue
        url = clean_url(href)
        if not url:
            continue
        img = it.select_one("img[alt]")
        alt = clean(img.get("alt") if img else None)
        name = alt if alt and alt.lower() not in ("portfolio", "logo", "image") else name_from_url(url)
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
