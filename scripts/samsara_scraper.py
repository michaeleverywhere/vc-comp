#!/usr/bin/env python3
"""Samsara BioCapital portfolio scraper -> samsara_companies.json
Source: https://www.samsaracap.com/portfolio/ — WordPress/Elementor page; each
.portfolio-item container holds the company name (heading) and a description
(text-editor widget). Samsara is a life-sciences fund, so the keyword tagger
usually yields BioTech/Health. No website, location, round, year or status
published on the page.
Empty descriptions filled from company websites (scripts/fill_descriptions_web.py)
are carried forward on re-runs.
"""
import os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, prune_substring_tags, apply_tag_overrides,
                             carry_forward_descriptions)
from _d20_common import write_out

SOURCE_URL = "https://www.samsaracap.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "samsara_companies.json")
PRIMARY = "Samsara BioCapital"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "A2 Biotherapeutics, Inc.": ["BioTech"],
    "Alamar Biosciences, Inc.": ["BioTech"],
    "Autobahn Labs, LLC": ["BioTech"],
    "Fluent Biosciences, Inc.": ["BioTech"],
    "Gossamer": ["BioTech"],
    "Inventiva": ["BioTech"],
    "Maro Bio": ["BioTech"],
    "Respira": ["BioTech"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio-item"):
        h = it.select_one(".elementor-heading-title")
        name = clean(h.get_text(" ")) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        txt = [clean(t.get_text(" ")) for t in it.select(".elementor-widget-text-editor") if clean(t.get_text(" "))]
        desc = " ".join(txt) or None
        tags = tags_for(name, desc)
        out.append({
            "company_name": name,
            "description": desc,
            "everywhere_tags": tags,
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for r in carry_forward_descriptions(out, OUT):  # filled earlier by fill_descriptions_web.py
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"))
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
