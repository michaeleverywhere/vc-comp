#!/usr/bin/env python3
"""Compound portfolio scraper -> compound_companies.json
Source: https://compound.vc/portfolio — Webflow .w-dyn-item cards
(name in .portfolio-text, company website on card link, category labels).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides, webflow_pages)
from _d20_common import write_out

SOURCE_URL = "https://compound.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "compound_companies.json")
PRIMARY = "Compound"
SECTOR_TAG_MAP = {
    "ai, machine learning, & robotics": ["Deeptech / Robotics / AR/VR", "Data & Analytics"],
    "automation": ["Deeptech / Robotics / AR/VR"],
    "fintech": ["Fintech"],
    "crypto & web3": ["Web3 / Crypto"],
    "biotech": ["BioTech / HealthTech"],
    "climate": ["Climate / Sustainability"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".w-dyn-item"):
            name_el = it.select_one(".portfolio-text, .heading-17")
            name = clean(name_el.get_text(" ")) if name_el else clean(it.get_text(" "))
            if not name or name.lower() in seen or len(name) > 80:
                continue
            # skip filter chrome
            if name.lower() in ("all", "companies", "automation"):
                continue
            seen.add(name.lower())
            url = None
            for a in it.select("a[href^=http]"):
                if "compound.vc" in a["href"] or is_social(a["href"]):
                    continue
                url = clean_url(a["href"])
                if url:
                    break
            cat_el = it.select_one(".portfolio-logo-category")
            sectors = [clean(cat_el.get_text(" "))] if cat_el and clean(cat_el.get_text(" ")) else []
            out.append({
                "company_name": name,
                "description": None,
                "company_url": url,
                "sectors": sectors,
                "everywhere_tags": tags_for(name, None, sectors, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
