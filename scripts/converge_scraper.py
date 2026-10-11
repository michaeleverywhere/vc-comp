#!/usr/bin/env python3
"""Converge portfolio scraper -> converge_companies.json
Source: https://converge.vc/portfolio/ — WordPress page; each company block
(.col-md-3 .inner) has the name (h2), a one-line description (p) and a
"Visit Site" link to the company website. No sector, location, round, year or
status labels are published on the page.
"""
import os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://converge.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "converge_companies.json")
PRIMARY = "Converge"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Loop": ["Logistics / Supply Chain"],
    "Pedestal AI": ["Data & Analytics"],
    "Rive AI": ["Deeptech / Robotics / AR/VR"],
    "Zeplyn": ["FinTech / Insurance"],
    "Crayon": ["Data & Analytics"],
    "Customily": ["Consumer"],
    "FeatureByte": ["Data & Analytics", "Dev Tools / Cloud"],
    "Guickly": ["Cybersecurity"],
    "Hark": ["Data & Analytics"],
    "Hologram": ["Dev Tools / Cloud"],
    "Incompass Labs": ["Future of Work"],
    "iRestify": ["PropTech"],
    "Loci Controls": ["Climate / Sustainability"],
    "Nift": ["Consumer"],
    "The Routing Company": ["Transportation / Mobility"],
    "Thoughtly": ["Future of Work"],
    "Amper": ["Deeptech / Robotics / AR/VR", "Data & Analytics"],
    "SyncOnSet": ["Gaming / Media / Entertainment"],
    "Visor": ["Future of Work"],
    "Ancestry": ["Consumer"],
    "OnDisplay": ["Data & Analytics"],
    "RapidMiner": ["Data & Analytics"],
    "Versata": ["Dev Tools / Cloud"],
    "VKernel": ["Dev Tools / Cloud"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio-title"):
        h = it.select_one("h2")
        name = clean(h.get_text(" ")) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        p = it.select_one("p")
        desc = clean(p.get_text(" ")) if p else None
        box = it.find_parent(class_="content")
        a = box.select_one("a.hidebtn[href]") if box else None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a else None,
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
