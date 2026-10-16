#!/usr/bin/env python3
"""Boost VC portfolio scraper -> boostvc_companies.json
Source: published Airtable proxy at boost-be.../api/airtable (fields Name,
One Liner, Website, Website Location, Year Invested, Website Category).
"""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.boost.vc/companies"
API = "https://boost-be-boosts-projects-a928d631.vercel.app/api/airtable"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "boostvc_companies.json")
PRIMARY = "Boost VC"
SECTOR_MAP = {
    "bio / health": ["BioTech", "Health"], "crypto": ["Web3 / Crypto"],
    "vr/ar": ["Deeptech / Robotics / AR/VR"], "space": ["Deeptech / Robotics / AR/VR"],
    "climate": ["Climate / Sustainability"], "ai": [], "other": [], "robotics": ["Deeptech / Robotics / AR/VR"],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    data = fetch(API, as_json=True)
    records = data.get("records", data) if isinstance(data, dict) else data
    out, seen = [], set()
    for rec in records or []:
        f = rec.get("fields") or rec
        name = clean(f.get("Name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(f.get("One Liner (Final)") or f.get("One Liner"))
        website = f.get("Website")
        if website:
            website = clean_url(website if str(website).startswith("http") else f"https://{website}")
        location = clean(f.get("Website Location"))
        year = f.get("Year Invested")
        try:
            year = int(year) if year else None
        except (TypeError, ValueError):
            year = None
        cats = f.get("Website Category") or []
        if isinstance(cats, str):
            cats = [cats]
        sectors = list(cats)
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": sectors,
            "location": location,
            "first_invested": year,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "sectors", "location", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
