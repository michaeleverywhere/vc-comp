#!/usr/bin/env python3
"""Version One Ventures portfolio scraper -> versionone_companies.json
Source: https://versionone.vc/portfolio/ — WP gallery items; names from captions / img alt.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://versionone.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "versionone_companies.json")
PRIMARY = "Version One Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".gallery-item"):
        cap = it.select_one(".wp-caption-text, .gallery-caption")
        img = it.select_one("img")
        name = clean(cap.get_text(" ")) if cap else None
        if not name and img:
            name = clean(img.get("alt"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        url = None
        a = it.select_one("a[href^=http]")
        if a and "versionone.vc" not in a["href"] and not is_social(a["href"]):
            url = clean_url(a["href"])
        # gallery links often point at the image itself — ignore media URLs
        if url and re.search(r"\.(png|jpg|jpeg|webp|svg|gif)(\?|$)", url, re.I):
            url = None
        if url and "wp-content/uploads" in url:
            url = None
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
