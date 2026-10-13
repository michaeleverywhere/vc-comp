#!/usr/bin/env python3
"""Sony Innovation Fund portfolio scraper -> sonyinnovation_companies.json
Source: https://www.sonyinnovationfund.com/portfolio/ — .portfolio-item list
(name in .title, website on card link, category CSS classes).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.sonyinnovationfund.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "sonyinnovation_companies.json")
PRIMARY = "Sony Innovation Fund"
SECTOR_TAG_MAP = {
    "ai": ["Data & Analytics"],
    "entertainment": ["Consumer"],
    "fintech": ["Fintech"],
    "medical": ["BioTech / HealthTech"],
    "iot": ["Deeptech / Robotics / AR/VR"],
    "deeptech": ["Deeptech / Robotics / AR/VR"],
    "climatetech": ["Climate / Sustainability"],
    "exit": [],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select("li.portfolio-item"):
        title = it.select_one("p.title, .title")
        name = clean(title.get_text(" ")) if title else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        a = it.select_one("a[href]")
        url = clean_url(a["href"]) if a and a.get("href") and not is_social(a["href"]) else None
        if url and "sonyinnovationfund.com" in url:
            url = None
        sectors = []
        status = None
        for cl in it.get("class") or []:
            if cl.startswith("categories-"):
                cat = cl.replace("categories-", "").replace("-", " ")
                if cat == "exit":
                    status = "acquired"
                else:
                    sectors.append(cat)
        out.append({
            "company_name": name,
            "description": None,
            "company_url": url,
            "sectors": sectors,
            "status": status,
            "everywhere_tags": tags_for(name, None, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("company_url", "status", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
