#!/usr/bin/env python3
"""Next Coast Ventures portfolio scraper -> nextcoast_companies.json
Source: https://www.nextcoastventures.com/portfolio — Webflow CMS list (single
page, all items). Each .mix.w-dyn-item has the name (h1.portfolio-item-heading),
a one-line description, the company website, a sector label (Enterprise /
Consumer / Emerging Platform) and a status label that is either blank or
"Sold". status: "Sold" -> acquired (site_status "Sold"); otherwise blank (the
site does not say active). No location, round or investment year published.
"""
import os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (webflow_pages, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides, is_social)
from _d20_common import write_out

SOURCE_URL = "https://www.nextcoastventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "nextcoast_companies.json")
PRIMARY = "Next Coast Ventures"
SECTOR_TAG_MAP = {"consumer": ["Consumer"]}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Arcade": ["Future of Work"],
    "BrainCheck": ["Health"],
    "Chargeback": ["FinTech / Insurance"],
    "Distribute": ["Data & Analytics"],
    "Localfluence, Inc": ["Consumer"],
    "Loman AI": ["Consumer"],
    "Propensity": ["Data & Analytics"],
    "Somite": ["BioTech"],
    "Street Smarts VR": ["Deeptech / Robotics / AR/VR", "RegTech/Gov/Legal"],
    "Submittable Holdings Inc.": ["Future of Work"],
    "Tenfold": ["Future of Work"],
    "Tiny Health": ["Health"],
    "TrustRadius": ["Data & Analytics"],
    "Vertalo": ["Web3 / Crypto", "FinTech / Insurance"],
    "Voxia": ["Future of Work"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".mix.w-dyn-item"):
            h = it.select_one(".portfolio-item-heading")
            name = clean(h.get_text(" ")) if h else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            d = it.select_one(".portfolio-item-description")
            desc = clean(d.get_text(" ")) if d else None
            w = it.select_one("a.portfolio-item-website[href]")
            site = clean_url(w["href"]) if w and not is_social(w["href"]) else None
            sec = it.select_one(".portfolio-item-sector")
            sectors = [clean(sec.get_text(" "))] if sec and clean(sec.get_text(" ")) else []
            st = it.select_one(".portfolio-item-status")
            st = clean(st.get_text(" ")) if st else None
            out.append({
                "company_name": name,
                "description": desc,
                "company_url": site,
                "sectors": sectors,
                "site_status": st,
                "status": "acquired" if (st or "").lower() == "sold" else None,
                "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
