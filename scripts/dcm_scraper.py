#!/usr/bin/env python3
"""DCM Ventures portfolio scraper -> dcm_companies.json
Source: https://www.dcm.com/companies — Webflow .portfolio-card with name,
sector label, and company website. Featured list (not exhaustive historical).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url,
                             prune_substring_tags, apply_tag_overrides, carry_forward_descriptions)
from _d20_common import write_out

SOURCE_URL = "https://www.dcm.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "dcm_companies.json")
PRIMARY = "DCM Ventures"
SECTOR_TAG_MAP = {
    "consumer": ["Consumer"], "fintech": ["FinTech / Insurance"],
    "frontier tech": ["Deeptech / Robotics / AR/VR"], "frontier": ["Deeptech / Robotics / AR/VR"],
    "enterprise": ["Future of Work", "Dev Tools / Cloud"], "healthcare": ["Health"],
    "crypto": ["Web3 / Crypto"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for card in soup.select(".portfolio-card"):
        a = card.select_one("a[href^=http]")
        txt = clean(card.get_text(" "))
        # text often "Name Sector"
        name, sector = None, None
        img = card.select_one("img[alt]")
        if img and img.get("alt"):
            name = clean(img.get("alt"))
        if not name and txt:
            # last word(s) may be sector
            for lab in ("Frontier Tech", "Fintech", "Consumer", "Enterprise", "Healthcare", "Crypto"):
                if txt.endswith(lab):
                    name = clean(txt[: -len(lab)])
                    sector = lab
                    break
            if not name:
                name = txt
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        if not sector and txt:
            for lab in ("Frontier Tech", "Fintech", "Consumer", "Enterprise", "Healthcare", "Crypto"):
                if lab.lower() in txt.lower():
                    sector = lab
                    break
        url = clean_url(a["href"]) if a else None
        sectors = [sector] if sector else []
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
    filled = carry_forward_descriptions(out, OUT)
    for r in out:
        if r.get("description"):
            r["everywhere_tags"] = tags_for(r["company_name"], r["description"], r.get("sectors"), SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "everywhere_tags"))
    if filled:
        print(f"  carried_forward_descriptions: {len(filled)}")


if __name__ == "__main__":
    main()
