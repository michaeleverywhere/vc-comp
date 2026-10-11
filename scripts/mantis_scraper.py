#!/usr/bin/env python3
"""Mantis VC portfolio scraper -> mantis_companies.json
Source: https://www.mantisvc.com/portfolio — Webflow page; each .portfolio-div
(a swiper slide; the list repeats some cards, deduped by name) has the company
name, a link to the company website and usually a one-line description. No
sector, location, round, year or status labels published.
"""
import os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides,
                             carry_forward_descriptions)
from _d20_common import write_out

SOURCE_URL = "https://www.mantisvc.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "mantis_companies.json")
PRIMARY = "Mantis VC"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Stability AI": ["Gaming / Media / Entertainment"],
    "Solve": ["Future of Work"],
    "Lemonslice AI": ["Data & Analytics"],
    "Product Science": ["Dev Tools / Cloud"],
    "Openlayer": ["Dev Tools / Cloud", "Data & Analytics"],
    "Certa": ["Future of Work"],
    "Monaco": ["Data & Analytics"],
    "Popmenu, Inc.": ["Consumer"],
    "Dandy": ["Health"],
    "Utilize Core": ["PropTech"],
    "Rangeview": ["Deeptech / Robotics / AR/VR"],
    "Verse": ["Health"],
    "c/side": ["Cybersecurity"],
    "Draftea": ["Gaming / Media / Entertainment"],
    "Portals": ["Gaming / Media / Entertainment", "Web3 / Crypto"],
    "Figment Inc.": ["Web3 / Crypto"],
    "Bego": ["Logistics / Supply Chain"],
    "MagicX Hero": ["Consumer"],
    "Synthesis": ["Consumer", "Future of Work"],
    "Pogo": ["Consumer", "FinTech / Insurance"],
    "Atlys": ["Consumer", "Transportation / Mobility"],
    "Knowde": ["Logistics / Supply Chain"],
    "Apeel": ["Climate / Sustainability", "CPG"],
    "Pledge": ["FinTech / Insurance"],
    "Projector": ["Dev Tools / Cloud"],
    "X1": ["Data & Analytics"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, idx = [], {}
    for it in soup.select(".portfolio-div"):
        n = it.select_one(".portfolio-company-name")
        name = clean(n.get_text(" ")) if n else None
        if not name:
            continue
        p = it.select_one("p")
        desc = clean(p.get_text(" ")) if p else None
        a = it.select_one("a[href]")
        site = clean_url(a["href"]) if a else None
        if site and site.startswith("http://") and "." in site:
            pass
        key = name.lower()
        if key in idx:
            r = idx[key]
            r["description"] = r["description"] or desc
            r["company_url"] = r["company_url"] or site
            continue
        r = {"company_name": name, "description": desc, "company_url": site,
             "everywhere_tags": [], "primary_investor": PRIMARY, "source_url": SOURCE_URL, "scraped_at": scraped_at}
        idx[key] = r
        out.append(r)
    carry_forward_descriptions(out, OUT)
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"))
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
