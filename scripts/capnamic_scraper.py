#!/usr/bin/env python3
"""Capnamic portfolio scraper -> capnamic_companies.json
Source: https://www.capnamic.com/portfolio — Webflow, every company row is in
the server HTML (expandable rows). Each row carries a metadata embed
(data-industry / data-stage / data-status / data-year), the city, a rich-text
description, Founders, Capnamic Team and Website / LinkedIn links.
data-year is the year Capnamic invested; data-stage the entry round.
Status: "Active" -> active, "Exit" -> acquired (raw kept in site_status).
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, stage_label, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.capnamic.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "capnamic_companies.json")
PRIMARY = "Capnamic"
SECTOR_TAG_MAP = {
    "software-as-a-service": [], "data": ["Data & Analytics"], "adtech": ["Gaming / Media / Entertainment"],
    "proptech": ["PropTech"], "marketplace": ["Consumer"], "fintech": ["FinTech / Insurance"],
    "insurtech": ["FinTech / Insurance"], "edtech": [], "robotics": ["Deeptech / Robotics / AR/VR"],
    "mobility": ["Transportation / Mobility"], "logistics": ["Logistics / Supply Chain"],
    "hr tech": ["Future of Work"], "process mining": ["Data & Analytics"],
}


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "GetSafe": ["FinTech / Insurance"],
    "Marta": ["Health", "Future of Work"],
    "Nanoleq": ["Health", "Consumer"],
    "NoMagic": ["Deeptech / Robotics / AR/VR", "Logistics / Supply Chain"],
    "QuantPi": ["Data & Analytics"],
    "Rex": ["Consumer"],
    "Wundertax": ["FinTech / Insurance"],
    "Zeotap": ["Gaming / Media / Entertainment", "Cybersecurity"],
    "cleverly": ["Consumer"],
    "everstox": ["Logistics / Supply Chain", "Consumer"],
    "how.fm": ["Future of Work"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for row in soup.select(".company-row-wrapper"):
        img = row.select_one("img.company-row-logo")
        name = clean(img.get("alt")) if img else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        md = row.select_one(".company-row-metadata") or {}
        metas = [clean(x.get_text()) for x in row.select(".company-row > .company-row-meta")]
        city = metas[1] if len(metas) > 1 and metas[1] else None
        d = row.select_one(".company-row-description")
        desc = clean(d.get_text(" ")) if d else None
        founders, team = [], []
        for blk in row.select(".company-row-team-block"):
            lab = clean(blk.select_one(".company-row-team-label").get_text()).lower() if blk.select_one(".company-row-team-label") else ""
            if lab.startswith("founder"):
                founders = [clean(p.get_text(" ")) for p in blk.select(".company-row-founders p") if clean(p.get_text(" "))]
            elif "team" in lab:
                team = [clean(x.get_text()) for x in blk.select(".w-dyn-item") if clean(x.get_text())]
        site = None
        for a in row.select("a.contact-link"):
            im = a.select_one("img")
            if im and "website" in (im.get("alt") or "").lower():
                site = clean_url(a.get("href"))
        raw_status = clean(md.get("data-status")) if md else None
        industry = clean(md.get("data-industry")) if md else None
        year = clean(md.get("data-year")) if md else None
        raw_stage = clean(md.get("data-stage")) if md else None
        sectors = [industry] if industry else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "status": {"active": "active", "exit": "acquired"}.get((raw_status or "").lower()),
            "site_status": raw_status,
            "stage": stage_label(raw_stage) if raw_stage and raw_stage != "-" else None,
            "first_invested": year if year and year.isdigit() else None,
            "location": city,
            "founders": founders,
            "capnamic_team": team,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "first_invested", "location", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
