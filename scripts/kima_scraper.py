#!/usr/bin/env python3
"""Kima Ventures portfolio scraper -> kima_companies.json
Source: https://www.kimaventures.com/portfolio — Next.js page whose
__NEXT_DATA__ (props.pageProps.companies) carries every portfolio company
(982 at first scrape): name, website, description, Kima sector labels and
country. The site publishes no stages, investment dates or exit statuses.
location = country as published by Kima.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://www.kimaventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "kima_companies.json")
PRIMARY = "Kima Ventures"
# Kima's own sector labels -> everywhere tags (labels with no clear match, e.g.
# SaaS / Mobile / Marketplace / Industry / Education, fall through to keywords)
SECTOR_TAG_MAP = {
    "finance": ["FinTech / Insurance"], "deeptech": ["Deeptech / Robotics / AR/VR"],
    "hardware / robotic": ["Deeptech / Robotics / AR/VR"], "health": ["Health"],
    "entertainment": ["Gaming / Media / Entertainment"], "media": ["Gaming / Media / Entertainment"],
    "gaming": ["Gaming / Media / Entertainment"], "cleantech": ["Climate / Sustainability"],
    "security": ["Cybersecurity"], "bitcoin": ["Web3 / Crypto"], "legaltech": ["RegTech/Gov/Legal"],
    "big data": ["Data & Analytics"], "api": ["Dev Tools / Cloud"], "e-commerce": ["Consumer"],
    "retail": ["Consumer"], "lifestyle": ["Consumer"], "social": ["Consumer"],
    "food/agritech": ["CPG"], "travel / tourism": ["Consumer"], "sharing economy": ["Consumer"],
}
TAG_OVERRIDES = {}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    data = json.loads(soup.select_one("#__NEXT_DATA__").string)
    rows = data["props"]["pageProps"]["companies"]
    if limit:
        rows = rows[:limit]
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for c in rows:
        name = clean(c.get("name"))
        if not name or c.get("id") in seen:
            continue
        seen.add(c.get("id"))
        desc = clean(c.get("description"))
        sectors = [clean(s.get("name")) for s in (c.get("sector") or []) if clean(s.get("name"))]
        country = (c.get("country") or {}).get("name")
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(c.get("url")),
            "sectors": sectors,
            "location": clean(country),
            "country_code": (c.get("country") or {}).get("code"),
            "everywhere_tags": tags_for(name, desc or "", sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "kima_id": c.get("id"),
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "sectors", "location", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
