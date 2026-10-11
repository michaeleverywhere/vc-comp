#!/usr/bin/env python3
"""Chicago Ventures portfolio scraper -> chicagoventures_companies.json
Source: https://www.chicagoventures.com/companies — Webflow CMS table
(paginated `?<hash>_page=N`). Columns: Industry, "Current Stage" (latest
funding round, e.g. Series B), "CV Invested" ("<YYYY>, <round>" = year Chicago
Ventures first invested and the round it entered at), Status (Active /
Acquired / ...), plus a description and a /company/<slug> link.
stage = Current Stage when it is a real round; entry round kept in
entry_stage; first_invested = the CV Invested year. status: Active -> active,
Acquired -> acquired, anything else kept only in site_status.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (webflow_pages, clean, tags_for, year_of, stage_label,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.chicagoventures.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "chicagoventures_companies.json")
PRIMARY = "Chicago Ventures"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "insurance": ["FinTech / Insurance"], "healthcare": ["Health"],
    "proptech": ["PropTech"], "construction": ["PropTech"], "legal": ["RegTech/Gov/Legal"],
    "mobility": ["Transportation / Mobility"], "travel": ["Consumer"], "gaming": ["Gaming / Media / Entertainment"],
    "consumer media & entertainment": ["Gaming / Media / Entertainment", "Consumer"],
    "supply chain, logistics & warehousing": ["Logistics / Supply Chain"], "energy": ["Climate / Sustainability"],
    "workforce management": ["Future of Work"], "productivity tools": ["Future of Work"],
    "education": ["Future of Work"], "data management": ["Data & Analytics"], "cybersecurity": ["Cybersecurity"],
    "food & beverage": ["CPG"], "cpg": ["CPG"], "e-commerce": ["Consumer"], "consumer": ["Consumer"],
}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Blitsy": ["Consumer"],
    "Catalytic": ["Future of Work"],
    "Curbside": ["Consumer"],
    "Interior Define": ["Consumer"],
    "Luxury Garage Sale": ["Consumer"],
    "Meta SaaS": ["Dev Tools / Cloud"],
    "Olive": ["Future of Work"],
    "Promenade": ["Consumer"],
    "Troops": ["Future of Work"],
    "Ureeka": ["Future of Work"],
    "ZenBusiness": ["Future of Work", "RegTech/Gov/Legal"],
    "Spring": ["Consumer"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".project-index-wrap.w-dyn-item"):
            t = it.select_one(".project-index_title")
            name = clean(t.get_text(" ")) if t else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            hdr = it.select_one(".project-index_item-header")
            ind = it.select_one("[fs-cmsfilter-field=Industry]")
            sectors = [clean(ind.get_text(" "))] if ind and clean(ind.get_text(" ")) else []
            cells = hdr.select(":scope > .project-index_cell") if hdr else []
            vals = []
            for c in cells:
                kids = [k for k in c.find_all("div", recursive=False)
                        if "project-info-mobile" not in (k.get("class") or []) and k.get("fs-cmsfilter-field") != "Industry"]
                vals.append(clean(kids[0].get_text(" ")) if kids else None)
            # cells: [industry cell, current stage, cv invested, status]
            current = vals[1] if len(vals) > 1 else None
            invested = vals[2] if len(vals) > 2 else None
            site_status = vals[3] if len(vals) > 3 else None
            entry = clean(re.sub(r"^\s*\d{4}\s*,?", "", invested or "")) if invested else None
            d = it.select_one(".project-index_item-description")
            desc = clean(d.get_text(" ")) if d else None
            a = it.select_one("a[href^='/company/']")
            st = (site_status or "").lower()
            out.append({
                "company_name": name,
                "description": desc,
                "sectors": sectors,
                "stage": stage_label(current),
                "current_stage_label": current,
                "entry_stage": stage_label(entry),
                "first_invested": year_of(invested),
                "site_status": site_status,
                "status": "active" if st == "active" else ("acquired" if st == "acquired" else None),
                "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "profile_url": urljoin(SOURCE_URL, a["href"]) if a else None,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "sectors", "stage", "entry_stage", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
