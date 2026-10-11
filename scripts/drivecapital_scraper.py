#!/usr/bin/env python3
"""Drive Capital portfolio scraper -> drivecapital_companies.json
Source: https://drivecapital.com/portfolio — Next.js (Contentful) site. The list
page's __NEXT_DATA__ (pageProps.portfolioList) gives every company's name, slug,
status (Active / IPO / Exit) and industry filter. Each detail page
(/portfolio/<slug>) has __NEXT_DATA__ pageProps.portfolioBioData.hero with the
description, the "VIEW WEBSITE" link and mediaAnnotation.city (HQ city).
status: Active -> active; IPO / Exit kept verbatim in site_status (Drive does not
say "acquired"). No round or investment year published.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, fetch_many, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://drivecapital.com/portfolio"
BASE = "https://drivecapital.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "drivecapital_companies.json")
PRIMARY = "Drive Capital"
SECTOR_TAG_MAP = {
    "healthcare": ["Health"], "fintech": ["FinTech / Insurance"], "future of work": ["Future of Work"],
    "robotics": ["Deeptech / Robotics / AR/VR"], "cybersecurity": ["Cybersecurity"],
    "edtech": ["Future of Work"], "content": ["Gaming / Media / Entertainment"],
}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Yolando": ["Data & Analytics"],
    "Sparx": ["FinTech / Insurance"],
    "Hallow": ["Consumer"],
    "Encamp": ["Climate / Sustainability", "RegTech/Gov/Legal"],
    "Lunasonde": ["Deeptech / Robotics / AR/VR"],
    "Hologram": ["Dev Tools / Cloud"],
    "StrongArm Technologies": ["Deeptech / Robotics / AR/VR", "Future of Work"],
    "Duality": ["Deeptech / Robotics / AR/VR"],
    "Physna": ["Deeptech / Robotics / AR/VR", "Data & Analytics"],
    "Stateless": ["Dev Tools / Cloud"],
    "Algolux": ["Deeptech / Robotics / AR/VR", "Transportation / Mobility"],
}


def next_data(html):
    tag = BeautifulSoup(html, "html.parser").find("script", id="__NEXT_DATA__")
    return json.loads(tag.string)["props"]["pageProps"] if tag and tag.string else {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    lst = next_data(fetch(SOURCE_URL)).get("portfolioList") or []
    urls = {x["slug"]: BASE + x["slug"] for x in lst if x.get("slug")}
    pages = fetch_many(list(urls.values()), workers=6)
    out, seen = [], set()
    for x in lst:
        name = clean(x.get("title"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        hero = x.get("hero") or {}
        st = ", ".join(hero.get("status") or []) or None
        sectors = [clean(i.get("filterValue")) for i in ((hero.get("filters") or {}).get("items") or [])
                   if i.get("filterLabel") == "industry" and clean(i.get("filterValue"))]
        desc = site = city = None
        html = pages.get(urls.get(x.get("slug")))
        if html:
            h = (next_data(html).get("portfolioBioData") or {}).get("hero") or {}
            desc = clean(h.get("description"))
            for c in ((h.get("ctasCollection") or {}).get("items") or []):
                if "website" in (c.get("text") or "").lower() and c.get("url"):
                    site = clean_url(c["url"])
                    break
            city = clean((h.get("mediaAnnotation") or {}).get("city"))
            st = ", ".join(h.get("status") or []) or st
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "sectors": [s for s in sectors if s != "Other"],
            "location": city,
            "site_status": st,
            "status": "active" if (st or "").lower() == "active" else None,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": urls.get(x.get("slug")),
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
