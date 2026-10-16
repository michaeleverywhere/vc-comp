#!/usr/bin/env python3
"""Dragonfly portfolio scraper -> dragonfly_companies.json
Source: https://dragonfly.com (portfolio) — Nuxt __NUXT_DATA__ embedded
Sanity portfolioItem records (title, description, category, external link).
"""
import os, re, sys, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.dragonfly.xyz/portfolio"
# site redirects to dragonfly.com
FETCH_URL = "https://dragonfly.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "dragonfly_companies.json")
PRIMARY = "Dragonfly"
SECTOR_MAP = {
    "defi": ["Web3 / Crypto", "FinTech / Insurance"],
    "stablecoin": ["Web3 / Crypto", "FinTech / Insurance"],
    "l1 / l2s": ["Web3 / Crypto"],
    "l1-l2s": ["Web3 / Crypto"],
    "infrastructure": ["Web3 / Crypto", "Dev Tools / Cloud"],
    "nft": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
    "cefi": ["Web3 / Crypto", "FinTech / Insurance"],
}
TAG_OVERRIDES = {}


def resolve(data, idx, depth=0, seen=None):
    if seen is None:
        seen = set()
    if not isinstance(idx, int) or idx < 0 or idx >= len(data):
        return idx
    if idx in seen or depth > 14:
        return None
    seen.add(idx)
    v = data[idx]
    if isinstance(v, dict):
        return {k: resolve(data, val, depth + 1, seen.copy()) for k, val in v.items()}
    if isinstance(v, list):
        return [resolve(data, x, depth + 1, seen.copy()) for x in v]
    return v


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(FETCH_URL)
    m = re.search(r'__NUXT_DATA__[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("no __NUXT_DATA__")
    data = json.loads(m.group(1))
    pi_type = next((i for i, x in enumerate(data) if x == "portfolioItem"), None)
    if pi_type is None:
        raise SystemExit("no portfolioItem type")
    out, seen = [], set()
    for i, x in enumerate(data):
        if not isinstance(x, dict) or x.get("_type") != pi_type:
            continue
        obj = resolve(data, i)
        if not isinstance(obj, dict):
            continue
        name = clean(obj.get("title"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(obj.get("description"))
        link = obj.get("link") or {}
        website = clean_url(link.get("linkHref")) if isinstance(link, dict) else None
        cat = clean(obj.get("categoryLabel") or obj.get("category") or obj.get("subtitle"))
        sectors = [cat] if cat else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
