#!/usr/bin/env python3
"""GroundUp Ventures portfolio scraper -> groundup_companies.json
Source: https://www.groundup.vc/portfolio — Webflow CMS (single page, 58
`div.gp-card` items). Each card has a one-line description and a lightbox with
company name, Overview, Sector, Location (US / Israel / Other), Current Stage,
Stage Invested, CEO, website ("Visit Site") and an acquisition block
("Acquired by X").
stage = Current Stage when it is a funding round (Pre-Seed ... Series E,
Pre-IPO); stage_invested = Stage Invested (entry round). "Exit" or an
acquisition block naming an acquirer -> status acquired. "Other" locations
are left blank.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, stage_label, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.groundup.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "groundup_companies.json")
PRIMARY = "GroundUp Ventures"
SECTOR_TAG_MAP = {
    "deep tech": ["Deeptech / Robotics / AR/VR"], "commerce & logistics": ["Logistics / Supply Chain"],
    "built environment": ["PropTech"], "finance & payments": ["FinTech / Insurance"],
    "security & fraud": ["Cybersecurity"], "data & infrastructure": ["Dev Tools / Cloud"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Axo Neurotech": [
        "Deeptech / Robotics / AR/VR",
        "Health"
    ],
    "Baba": [
        "Health",
        "Consumer"
    ],
    "BuildOps": [
        "PropTech",
        "Future of Work"
    ],
    "Covenant": [
        "Deeptech / Robotics / AR/VR",
        "RegTech/Gov/Legal"
    ],
    "Dandelion": [
        "Climate / Sustainability",
        "PropTech"
    ],
    "Dialogue": [
        "Consumer"
    ],
    "Disco": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "EliseAI": [
        "PropTech",
        "Health",
        "Future of Work"
    ],
    "Flyp": [
        "Consumer",
        "Future of Work"
    ],
    "Fondue": [
        "Consumer",
        "FinTech / Insurance"
    ],
    "G2 Systems": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Harbinger": [
        "Transportation / Mobility",
        "Climate / Sustainability"
    ],
    "HyWatts": [
        "Climate / Sustainability"
    ],
    "Jones": [
        "PropTech",
        "RegTech/Gov/Legal"
    ],
    "Kela": [
        "Deeptech / Robotics / AR/VR",
        "RegTech/Gov/Legal"
    ],
    "Konko": [
        "Health",
        "Future of Work"
    ],
    "Lenkie": [
        "FinTech / Insurance"
    ],
    "Ninja": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "OurRitual": [
        "Health",
        "Consumer"
    ],
    "Panjaya": [
        "Gaming / Media / Entertainment"
    ],
    "PDQ": [
        "Consumer"
    ],
    "Pipe": [
        "FinTech / Insurance"
    ],
    "Portless": [
        "Logistics / Supply Chain",
        "Consumer"
    ],
    "Postscript": [
        "Consumer"
    ],
    "PropheX": [
        "BioTech",
        "Data & Analytics"
    ],
    "Reap": [
        "Health",
        "FinTech / Insurance"
    ],
    "Starcloud": [
        "Deeptech / Robotics / AR/VR",
        "Dev Tools / Cloud"
    ],
    "TermScout": [
        "RegTech/Gov/Legal",
        "Data & Analytics"
    ],
    "The Lithium Company": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Threefold": [
        "RegTech/Gov/Legal"
    ],
    "Tolstoy": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "Triple Whale": [
        "Data & Analytics",
        "Consumer"
    ],
    "Unit AI Labs": [
        "Deeptech / Robotics / AR/VR",
        "Logistics / Supply Chain"
    ],
    "Upfort": [
        "Cybersecurity",
        "FinTech / Insurance"
    ],
    "Weave Bio": [
        "BioTech",
        "RegTech/Gov/Legal"
    ],
    "Western Chemicals": [
        "Climate / Sustainability"
    ],
    "Younity": [
        "PropTech"
    ],
    "ZeroMark": [
        "Deeptech / Robotics / AR/VR",
        "RegTech/Gov/Legal"
    ],
    "Glass Imaging": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Hello Wonder": [
        "Consumer"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for c in soup.select("div.gp-card.w-dyn-item"):
        n = c.select_one(".portfolio-lightbox .company-name")
        name = clean(n.get_text(" ")) if n else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        f = {}
        for w in c.select(".portfolio-lightbox .tags-wrapper, .portfolio-lightbox .ceo-tag-wrapper"):
            lab, val = w.select_one(".tag-lightbox"), w.select_one(".tag-text")
            if lab and val and clean(val.get_text(" ")):
                f[clean(lab.get_text(" ")).lower()] = clean(val.get_text(" "))
        ov = c.select_one(".overview-text")
        overview = clean(ov.get_text(" ")) if ov else None
        sd = c.select_one(".gp-card-description")
        short = clean(sd.get_text(" ")) if sd else None
        site = next((a["href"] for a in c.select("a.lightbox-links[href^=http]") if "visit" in a.get_text(" ").lower()), None)
        acq_name = c.select_one(".gp-cms-acquirer-name")
        acquirer = clean(acq_name.get_text(" ")) if acq_name else None
        cur = f.get("current stage")
        loc = f.get("location")
        sectors = [f["sector"]] if f.get("sector") else []
        acquired = bool(acquirer) or (cur or "").lower() == "exit"
        out.append({
            "company_name": name,
            "description": overview or short,
            "tagline": short,
            "company_url": clean_url(site) if site else None,
            "status": "acquired" if acquired else None,
            "site_status": cur,
            "acquirer": acquirer,
            "stage": stage_label(cur),
            "stage_invested": stage_label(f.get("stage invested")),
            "location": loc if loc and loc.lower() != "other" else None,
            "ceo": f.get("ceo"),
            "sectors": sectors,
            "everywhere_tags": tags_for(name, " ".join(x for x in (short, overview) if x), sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "acquirer", "stage", "stage_invested", "location", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
