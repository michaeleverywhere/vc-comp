#!/usr/bin/env python3
"""Bonfire Ventures portfolio scraper -> bonfire_companies.json
Source: https://bonfirevc.com/companies — Webflow CMS list (.w-dyn-item) with
name, tagline, founders, location, industry, partnered year, stage, website.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides, stage_label
from _d20_common import write_out

SOURCE_URL = "https://bonfirevc.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "bonfire_companies.json")
PRIMARY = "Bonfire Ventures"
SECTOR_MAP = {
    "fintech": ["FinTech / Insurance"], "health": ["Health"], "healthcare": ["Health"],
    "enterprise": [], "consumer": ["Consumer"], "climate": ["Climate / Sustainability"],
    "security": ["Cybersecurity"], "cybersecurity": ["Cybersecurity"],
    "devtools": ["Dev Tools / Cloud"], "developer tools": ["Dev Tools / Cloud"],
    "ai": [], "infrastructure": ["Dev Tools / Cloud"], "saas": [],
}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".w-dyn-item"):
        name_el = it.select_one(".paragraph-3xl")
        name = clean(name_el.get_text(" ")) if name_el else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        tagline_el = it.select_one(".company-tagline-tablet, .company-description-wrapper .paragraph-base")
        desc = clean(tagline_el.get_text(" ")) if tagline_el else None
        # labeled fields
        fields = {}
        for grid in it.select(".companiespage-grid-content"):
            label = clean(grid.get_text(" ").split("\n")[0] if False else None)
            # structure: small label text then paragraph-small value
            texts = [clean(t) for t in grid.stripped_strings]
            texts = [t for t in texts if t]
            if len(texts) >= 2:
                fields[texts[0].lower()] = texts[-1]
            elif len(texts) == 1:
                pass
        location = fields.get("location")
        industry = fields.get("industry")
        partnered = fields.get("partnered")
        stage_raw = fields.get("stage")
        website = None
        for a in it.select("a[href]"):
            href = a.get("href") or ""
            label = clean(a.get_text(" ")) or ""
            if label.lower() == "website" and href.startswith("http"):
                website = clean_url(href)
                break
        year = int(partnered) if partnered and re.fullmatch(r"(19|20)\d\d", partnered) else None
        stage = None
        if stage_raw and not re.search(r"(?i)early.?stage|growth|late", stage_raw or ""):
            stage = stage_label(stage_raw)
        # Bonfire's "Early Stage" is not a funding round — leave blank
        sectors = [industry] if industry else []
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "sectors": sectors,
            "location": location,
            "stage": stage,
            "first_invested": year,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "location", "sectors", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
