#!/usr/bin/env python3
"""Commerce Ventures portfolio scraper -> commerceventures_companies.json
Source: https://commerce.vc/portfolio/ — .portfolio anchors; names from domain / logo filename.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlsplit, unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://commerce.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "commerceventures_companies.json")
PRIMARY = "Commerce Ventures"
SECTOR_TAG_MAP = {"fintech": ["Fintech"]}
TAG_OVERRIDES = {}


def name_from(url, img):
    if img and img.get("alt"):
        n = clean(img["alt"])
        if n and n.lower() not in ("logo", "image"):
            return n
    if url:
        host = urlsplit(url).netloc.lower().removeprefix("www.")
        base = host.split(".")[0].replace("-", " ").title()
        return clean(base)
    if img and img.get("src"):
        src = unquote(img["src"])
        m = re.search(r"/([^/]+)\.(?:png|jpg|jpeg|webp|svg)", src, re.I)
        if m:
            slug = re.sub(r"[-_]?(logo|Logo|Screenshot|at-\d+|300x\d+|new|white|black)", " ", m.group(1))
            slug = clean(slug.replace("-", " ").replace("_", " "))
            if slug and len(slug) > 1:
                return slug
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio"):
        a = it if it.name == "a" and it.get("href") else it.select_one("a[href]")
        href = a.get("href") if a else None
        url = clean_url(href) if href and href.startswith("http") and "commerce.vc" not in href and not is_social(href) else None
        img = it.select_one("img")
        name = name_from(url, img)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        sectors = ["Fintech"]
        out.append({
            "company_name": name,
            "description": None,
            "company_url": url,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, None, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
