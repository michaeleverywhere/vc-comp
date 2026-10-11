#!/usr/bin/env python3
"""Stage 2 Capital portfolio scraper -> stage2_companies.json
Source: https://www.stage2.capital/portfolio — HubSpot page; every portfolio card
(<a class="portfolio-card">) carries data-* attributes: name, link (company
website), industry (comma list), founders, data-description (= HQ location),
data-why-invested (URL-encoded HTML company blurb), data-year-invested and
data-year-founded — which on this site holds the funding round Stage 2 entered
at (Pre-Seed / Seed / Series A / Series B) or is blank. Stage only from that
round label (never from a year). No status published.
"""
import json, os, sys
from datetime import datetime, timezone
from urllib.parse import unquote_plus

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, html_text, tags_for, clean_url, year_of, stage_label,
                             prune_substring_tags, apply_tag_overrides)

SOURCE_URL = "https://www.stage2.capital/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "stage2_companies.json")
PRIMARY = "Stage 2 Capital"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "hr": ["Future of Work"], "security": ["Cybersecurity"],
    "data & infrastructure": ["Data & Analytics", "Dev Tools / Cloud"], "developer tools": ["Dev Tools / Cloud"],
    "collaboration & productivity": ["Future of Work"], "healthcare": ["Health"], "health": ["Health"],
    "proptech": ["PropTech"], "legal": ["RegTech/Gov/Legal"], "supply chain": ["Logistics / Supply Chain"],
}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Arda": ["Logistics / Supply Chain"],
    "Auxia": ["Data & Analytics"],
    "DayAI": ["Future of Work"],
    "Haizelabs": ["Cybersecurity", "Dev Tools / Cloud"],
    "MVP Match": ["Future of Work"],
    "PartnerPortal": ["Future of Work"],
    "Sendoso": ["Consumer"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for c in soup.select(".portfolio-card[data-name]"):
        name = clean(c.get("data-name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc_html = unquote_plus(c.get("data-why-invested") or "")
        desc = html_text(desc_html)
        if desc:
            desc = clean(desc.replace("Read why we invested here", ""))
        sectors = [clean(x) for x in (c.get("data-industry") or "").split(",") if clean(x)]
        founders = [clean(x) for x in (c.get("data-founders") or "").split(",") if clean(x)]
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": clean_url(c.get("data-link")),
            "sectors": sectors,
            "location": clean(c.get("data-description")),
            "stage": stage_label(c.get("data-year-founded")),
            "first_invested": year_of(c.get("data-year-invested")),
            "status": None,
            "founders": founders,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "stage", "first_invested", "location", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
