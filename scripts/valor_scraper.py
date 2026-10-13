#!/usr/bin/env python3
"""Valor Equity Partners portfolio scraper -> valor_companies.json
Source: https://www.valorep.com/growth-investments — Squarespace image slides
(name from img alt, website from slide anchor; careers URLs trimmed to origin).
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urlsplit, urlunsplit
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.valorep.com/growth-investments"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "valor_companies.json")
PRIMARY = "Valor Equity Partners"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def company_home(url):
    u = clean_url(url)
    if not u:
        return None
    parts = urlsplit(u)
    # drop /careers paths — still the company site
    if re.search(r"/(careers|jobs|job-openings)(/|$)", parts.path, re.I):
        return urlunsplit((parts.scheme, parts.netloc, "/", "", ""))
    # valorep internal pages are not company sites
    if "valorep.com" in parts.netloc:
        return None
    return u


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a.image-slide-anchor[href]"):
        img = a.find("img")
        name = clean(img.get("alt") if img else None)
        if not name or name.lower() in seen:
            continue
        # skip decorative
        if name.lower().endswith(".png") or name.lower().endswith(".svg"):
            continue
        seen.add(name.lower())
        url = company_home(a.get("href"))
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
