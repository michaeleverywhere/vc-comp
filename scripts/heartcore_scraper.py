#!/usr/bin/env python3
"""Heartcore Capital portfolio scraper -> heartcore_companies.json
Source: https://www.heartcore.com/companies — Webflow CMS table (Finsweet
filters), server-rendered across Webflow pagination pages. Each row: company
name, website link, category, country, year (Heartcore's investment year,
e.g. Reddit 2013) and status (Active / Exit). Undisclosed "Stealth" rows are
skipped (no company identity). The site publishes no descriptions or
stages; descriptions may later be filled from company websites by
scripts/fill_descriptions_web.py (carried forward here, never invented).
Status: Active -> active; Exit -> acquired (raw kept in site_status).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, tags_for, clean_url, carry_forward_descriptions, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.heartcore.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "heartcore_companies.json")
PRIMARY = "Heartcore Capital"
SECTOR_TAG_MAP = {
    "defence": ["RegTech/Gov/Legal", "Deeptech / Robotics / AR/VR"], "quantum": ["Deeptech / Robotics / AR/VR"],
    "robotics": ["Deeptech / Robotics / AR/VR"], "space": ["Deeptech / Robotics / AR/VR"],
    "data analytics": ["Data & Analytics"], "synbio": ["BioTech"], "web3": ["Web3 / Crypto"],
    "ecommerce": ["Consumer"], "retail": ["Consumer"], "productivity": ["Future of Work"],
    "mobility": ["Transportation / Mobility"], "housing": ["PropTech"], "health and wellness": ["Health"],
    "food": ["CPG"], "finance and insurance": ["FinTech / Insurance"], "energy": ["Climate / Sustainability"],
    "travel": ["Consumer"], "entertainment": ["Gaming / Media / Entertainment"], "education": ["Future of Work"],
}
STATUS = {"active": "active", "exit": "acquired", "exited": "acquired"}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Fast Travel Games": ["Gaming / Media / Entertainment"],
    "FlexAI": ["Dev Tools / Cloud"],
    "Kaisa": ["Data & Analytics"],
    "Kontakt.io": ["Health", "Data & Analytics"],
    "Layerise": ["Data & Analytics"],
    "PhaseTree": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Quesma": ["Dev Tools / Cloud"],
    "Spinnable AI": ["Future of Work"],
    "Voyfai": ["Logistics / Supply Chain"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for r in soup.select(".portfolio__tr"):
            n = r.select_one('[fs-cmssort-field="company"]')
            name = clean(n.get_text(" ")) if n else None
            if not name or name.lower() == "stealth" or name.lower() in seen:
                continue
            seen.add(name.lower())
            g = lambda k: clean(r.select_one(f'[fs-cmsfilter-field="{k}"]').get_text(" ")) if r.select_one(f'[fs-cmsfilter-field="{k}"]') else None
            cats = [clean(x.get_text(" ")) for x in r.select('[fs-cmsfilter-field="category"]')]
            countries = [clean(x.get_text(" ")) for x in r.select('[fs-cmsfilter-field="country"]')]
            site = next((a["href"] for a in r.select("a[href^=http]")), None)
            prof = next((a["href"] for a in r.select('a[href^="/companies/"]')), None)
            year, raw_status = g("year"), g("status")
            out.append({
                "company_name": name,
                "description": None,
                "company_url": clean_url(site),
                "company_profile_url": ("https://www.heartcore.com" + prof) if prof else None,
                "status": STATUS.get((raw_status or "").lower()),
                "site_status": raw_status,
                "first_invested": int(year) if year and re.fullmatch(r"\d{4}", year) else None,
                "location": ", ".join(c for c in countries if c) or None,
                "sectors": [c for c in cats if c and c != "Other"],
                "everywhere_tags": tags_for(name, None, cats, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
            if limit and len(out) >= limit:
                break
    for r in carry_forward_descriptions(out, OUT):
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"], r["sectors"], SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "first_invested", "location", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
