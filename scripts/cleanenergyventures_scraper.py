#!/usr/bin/env python3
"""Clean Energy Ventures portfolio scraper -> cleanenergyventures_companies.json
Source: https://cleanenergyventures.com/portfolio — Webflow page; each
.company-card has the name (h2.company-name), a sector badge (Industrial / Grid
/ Buildings / Mobility / ...), a description, the company website (first link)
and a "Co-investors" list (kept as co_investors). Every company is a climate-
technology investment (the fund's mandate), so Climate / Sustainability is
always one of the tags. No location, round, year or status published.
"""
import os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://cleanenergyventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "cleanenergyventures_companies.json")
PRIMARY = "Clean Energy Ventures"
SECTOR_TAG_MAP = {
    "mobility": ["Transportation / Mobility"], "buildings": ["PropTech"],
    "industrial": ["Deeptech / Robotics / AR/VR"], "agriculture": ["CPG"], "food & agriculture": ["CPG"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".company-card"):
        n = it.select_one(".company-name")
        name = clean(n.get_text(" ")) if n else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        d = it.select_one(".company-description")
        desc = clean(d.get_text(" ")) if d else None
        b = it.select_one(".sector-badge")
        sectors = [clean(b.get_text(" "))] if b and clean(b.get_text(" ")) else []
        a = it.select_one("a[href]")
        co = [clean(x.get_text(" ")) for x in it.select(".card-investors a") if clean(x.get_text(" "))]
        tags = tags_for(name, desc, sectors, SECTOR_TAG_MAP)
        if "Climate / Sustainability" not in tags:
            tags = (["Climate / Sustainability"] + tags)[:4]
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a else None,
            "sectors": sectors,
            "co_investors": co,
            "everywhere_tags": tags,
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "co_investors", "everywhere_tags"))


if __name__ == "__main__":
    main()
