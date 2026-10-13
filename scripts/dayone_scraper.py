#!/usr/bin/env python3
"""Day One Ventures portfolio scraper -> dayone_companies.json
Source: https://www.dayoneventures.com/ — Next.js __NEXT_DATA__ data.companies
(domain, mission, category, exit flag, person). Names derived from domain.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.dayoneventures.com/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "dayone_companies.json")
PRIMARY = "Day One Ventures"
SECTOR_TAG_MAP = {
    "ai": ["Data & Analytics"],
    "future of work": ["Enterprise / SaaS"],
    "enterprise": ["Enterprise / SaaS"],
    "consumer": ["Consumer"],
    "fintech": ["Fintech"],
    "health": ["BioTech / HealthTech"],
    "climate": ["Climate / Sustainability"],
    "crypto": ["Web3 / Crypto"],
}
TAG_OVERRIDES = {}


def name_from_domain(domain):
    d = (domain or "").lower().removeprefix("www.")
    base = d.split(".")[0]
    # common multi-word brands kept as title case of slug
    return clean(base.replace("-", " ").title())


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("FATAL: no __NEXT_DATA__ on Day One")
    nd = json.loads(m.group(1))
    comps = nd["props"]["pageProps"]["data"]["companies"]
    out, seen = [], set()
    for c in comps:
        domain = clean(c.get("domain"))
        name = name_from_domain(domain)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(c.get("mission"))
        cat = (c.get("category") or {})
        sector = clean(cat.get("title")) if isinstance(cat, dict) else None
        sectors = [sector] if sector else []
        status = "acquired" if c.get("exit") is True else ("active" if c.get("exit") is False else None)
        url = clean_url("https://" + domain) if domain else None
        founders = []
        person = clean(c.get("person"))
        if person:
            founders = [clean(p) for p in re.split(r"\s*/\s*|\s+and\s+", person) if clean(p)]
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": url,
            "sectors": sectors,
            "status": status,
            "founders": founders,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
