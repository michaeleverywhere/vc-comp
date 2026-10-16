#!/usr/bin/env python3
"""Hiro Capital portfolio scraper -> hiro_companies.json
Source: https://hiro.capital/companies — cards like "Islo AI 2022" linking out.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, is_social, year_of
from _d20_common import write_out

SOURCE_URL = "https://hiro.capital/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "hiro_companies.json")
PRIMARY = "Hiro Capital"
SECTOR_MAP = {
    "ai": [], "games": ["Gaming / Media / Entertainment"], "infrastructure": ["Dev Tools / Cloud"],
    "sports": ["Gaming / Media / Entertainment"], "spatial": ["Deeptech / Robotics / AR/VR"],
    "augmentation": ["Deeptech / Robotics / AR/VR"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href^=http]"):
        href = a["href"]
        if "hiro.capital" in href or is_social(href):
            continue
        text = clean(a.get_text(" "))
        if not text or text.lower().startswith("portfolio "):
            continue
        # "Name Sector · Sector Year" or "Name Sector Year"
        year = year_of(text)
        # strip trailing year
        core = re.sub(r"\s+(19|20)\d{2}\s*$", "", text).strip()
        # split name vs sectors: sectors are trailing known tokens
        sectors = []
        name = core
        for token in ("AI", "Games", "Infrastructure", "Sports", "Spatial", "Augmentation"):
            if re.search(rf"(?:·|\s){token}\b", core):
                sectors.append(token)
        # name is before first sector token
        m = re.split(r"\s+(?:AI|Games|Infrastructure|Sports|Spatial|Augmentation)\b", core, maxsplit=1)
        if m:
            name = clean(m[0])
        if not name or name.lower() in seen or len(name) > 60:
            continue
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": None,
            "company_url": clean_url(href),
            "sectors": sectors,
            "first_invested": year,
            "everywhere_tags": tags_for(name, None, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("company_url", "sectors", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
