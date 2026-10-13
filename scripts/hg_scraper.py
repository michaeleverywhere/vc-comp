#!/usr/bin/env python3
"""Hg portfolio scraper -> hg_companies.json
Source: https://hgcapital.com/portfolio — Next.js __NEXT_DATA__ total.items (titles)
plus featured companyCollection (description, country, founded, partnered year).
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://hgcapital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "hg_companies.json")
PRIMARY = "Hg"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("FATAL: no __NEXT_DATA__ on Hg portfolio")
    nd = json.loads(m.group(1))
    data = nd["props"]["pageProps"]["data"]
    featured = {c["title"]: c for c in (data.get("companyCollection") or {}).get("items") or []}
    titles = [x.get("title") for x in (data.get("total") or {}).get("items") or [] if x.get("title")]
    out, seen = [], set()
    for title in titles:
        name = clean(title)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        feat = featured.get(name) or {}
        desc = clean(feat.get("shortDescription"))
        sectors = list(feat.get("category") or []) if isinstance(feat.get("category"), list) else []
        loc = clean(feat.get("country"))
        first = clean(str(feat.get("partneredWithHg"))) if feat.get("partneredWithHg") else None
        # partnered year is not a funding round — store as first_invested year only
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": None,
            "sectors": sectors,
            "location": loc,
            "first_invested": first,
            "everywhere_tags": tags_for(name, desc, sectors),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "location", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
