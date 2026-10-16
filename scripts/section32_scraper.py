#!/usr/bin/env python3
"""Section 32 portfolio scraper -> section32_companies.json
Source: https://www.s32.com — Select Companies link list (name + website).
Caveat: featured/select subset only.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social
from _d20_common import write_out

SOURCE_URL = "https://www.s32.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "section32_companies.json")
PRIMARY = "Section 32"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a.companies_link[href]"):
        name = clean(a.get_text(" "))
        href = a.get("href") or ""
        if not name or not href.startswith("http") or is_social(href):
            continue
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": None,
            "company_url": clean_url(href),
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
