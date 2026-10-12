#!/usr/bin/env python3
"""HV Capital portfolio scraper -> hvcapital_companies.json
Source: https://www.hvcapital.com/portfolio — Framer companies table. Each
.__CompaniesTableListItem row has CellName, description, sector(s), and
Early/Growth label (not a funding round → STAGE blank). SSR exposes the
featured set; full historical list is client-filtered.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.hvcapital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "hvcapital_companies.json")
PRIMARY = "HV Capital"
SECTOR_TAG_MAP = {
    "ai & enterprise software": ["Data & Analytics", "Dev Tools / Cloud"],
    "ai and enterprise software": ["Data & Analytics", "Dev Tools / Cloud"],
    "deep tech": ["Deeptech / Robotics / AR/VR"],
    "cybersecurity": ["Cybersecurity"],
    "healthcare": ["Health"],
    "consumer": ["Consumer"],
    "fintech": ["FinTech / Insurance"],
    "resilience & defence": ["Deeptech / Robotics / AR/VR"],
    "resilience and defence": ["Deeptech / Robotics / AR/VR"],
    "climate": ["Climate / Sustainability"],
    "marketplace": ["Consumer"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for row in soup.select('[class$="__CompaniesTableListItem"]'):
        name_el = row.select_one('[class*="CellName"]')
        name = clean(name_el.get_text(" ")) if name_el else None
        cells = [clean(c.get_text(" ")) for c in row.select('[class*="__Cell"]')]
        cells = [c for c in cells if c]
        desc = cells[1] if len(cells) > 1 else None
        sector_raw = cells[2] if len(cells) > 2 else None
        stage_raw = cells[3] if len(cells) > 3 else None
        if not name and cells:
            name = cells[0]
        if not name or name.lower() in seen or len(name) > 60:
            continue
        seen.add(name.lower())
        sectors = [s.strip() for s in re.split(r"\s*\|\s*", sector_raw or "") if s.strip()]
        out.append({
            "company_name": name,
            "description": desc,
            "sectors": sectors,
            "site_stage": stage_raw,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
