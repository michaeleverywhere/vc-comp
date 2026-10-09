#!/usr/bin/env python3
"""Beringea portfolio scraper -> beringea_companies.json
Source: https://www.beringea.com/portfolio — Next.js page backed by Sanity;
the full investment list ships in __NEXT_DATA__ (page module "investments"):
company, strapline, link, sectors[].title, status (current / exited) and
fund (uk / us / uk_us — the Beringea fund that invested, shown on the card
as U.K. / U.S.; NOT the company's HQ, so it is kept as `fund`, not location).
No stage or investment year is published.
Status: current -> active; exited -> acquired (raw kept in site_status).
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.beringea.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "beringea_companies.json")
PRIMARY = "Beringea"
STATUS = {"current": "active", "exited": "acquired"}
FUND = {"uk": "UK", "us": "US", "uk_us": "UK & US"}
SECTOR_TAG_MAP = {
    "consumer": ["Consumer"], "healthcare": ["Health"], "health": ["Health"], "fintech": ["FinTech / Insurance"],
    "financial services": ["FinTech / Insurance"], "media": ["Gaming / Media / Entertainment"],
    "media & entertainment": ["Gaming / Media / Entertainment"], "cleantech": ["Climate / Sustainability"],
    "sustainability": ["Climate / Sustainability"], "edtech": ["Future of Work"], "education": ["Future of Work"],
    "proptech": ["PropTech"], "real estate": ["PropTech"], "cybersecurity": ["Cybersecurity"],
    "security": ["Cybersecurity"], "industrial": ["Deeptech / Robotics / AR/VR"], "clean technology": ["Climate / Sustainability"],
    "advanced manufacturing": ["Deeptech / Robotics / AR/VR"],
    "logistics": ["Logistics / Supply Chain"], "mobility": ["Transportation / Mobility"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "MAGIC AI": [
        "Consumer",
        "Health"
    ],
    "Kord": [
        "FinTech / Insurance",
        "RegTech/Gov/Legal"
    ],
    "Cycle Exchange": [
        "Consumer",
        "Transportation / Mobility"
    ],
    "Limitless Travel": [
        "Consumer",
        "Transportation / Mobility"
    ],
    "VRAI": [
        "Data & Analytics",
        "Deeptech / Robotics / AR/VR",
        "Future of Work"
    ],
    "MOTH": [
        "CPG",
        "Consumer"
    ],
    "Iceberg Data Lab": [
        "Climate / Sustainability",
        "Data & Analytics",
        "FinTech / Insurance"
    ],
    "Mojo": [
        "Health",
        "Consumer"
    ],
    "Andersen EV": [
        "Transportation / Mobility",
        "Climate / Sustainability"
    ],
    "Farmer J": [
        "Consumer"
    ],
    "Dentologie": [
        "Health"
    ],
    "Optilogic": [
        "Logistics / Supply Chain",
        "Dev Tools / Cloud"
    ],
    "DASH": [
        "CPG",
        "Consumer"
    ],
    "Authenticx": [
        "Data & Analytics",
        "Health"
    ],
    "Chattermill": [
        "Data & Analytics"
    ],
    "Gorilla": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Lucky Saint": [
        "CPG",
        "Consumer"
    ],
    "YardLink": [
        "Logistics / Supply Chain",
        "PropTech"
    ],
    "Tovala": [
        "Consumer",
        "CPG"
    ],
    "Rush ReCommerce": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "WiredScore": [
        "PropTech"
    ],
    "CGHero": [
        "Future of Work",
        "Gaming / Media / Entertainment"
    ],
    "Learnerbly": [
        "Future of Work"
    ],
    "Plank Hardware": [
        "Consumer"
    ],
    "LITTA": [
        "Consumer",
        "Climate / Sustainability"
    ],
    "Orbion Space Technology": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Moonshot": [
        "Data & Analytics",
        "Cybersecurity"
    ],
    "ASTERRA": [
        "Data & Analytics",
        "Deeptech / Robotics / AR/VR",
        "Climate / Sustainability"
    ],
    "Flywheel": [
        "Health",
        "Data & Analytics"
    ],
    "CreativeX": [
        "Data & Analytics",
        "Gaming / Media / Entertainment"
    ],
    "Social Value Portal": [
        "Data & Analytics",
        "Climate / Sustainability"
    ],
    "Commonplace": [
        "RegTech/Gov/Legal",
        "PropTech"
    ],
    "Micro-LAM": [
        "Deeptech / Robotics / AR/VR"
    ],
    "ATLAS Space Operations": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Arctic Shores": [
        "Future of Work"
    ],
    "RealTime Software Solutions": [
        "Health",
        "BioTech"
    ],
    "Festicket": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Avid Ratings": [
        "PropTech",
        "Data & Analytics"
    ],
    "Poq": [
        "Consumer",
        "Dev Tools / Cloud"
    ],
    "dscout": [
        "Data & Analytics"
    ],
    "Firefly": [
        "Future of Work"
    ],
    "MPB": [
        "Consumer"
    ],
    "Lumar": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
    "Zoovu": [
        "Consumer",
        "Dev Tools / Cloud"
    ],
    "Floyd": [
        "Consumer"
    ],
    "Arrive": [
        "Transportation / Mobility",
        "Logistics / Supply Chain"
    ],
    "Honeycomb": [
        "Gaming / Media / Entertainment"
    ],
    "ContactEngine": [
        "Future of Work"
    ],
    "D3O": [
        "Deeptech / Robotics / AR/VR",
        "Consumer"
    ],
    "Lantum": [
        "Health",
        "Future of Work"
    ],
    "Sealskinz": [
        "Consumer"
    ],
    "Perfect Channel": [
        "Consumer"
    ],
    "DIME": [
        "Gaming / Media / Entertainment",
        "Future of Work"
    ],
    "Rethink": [
        "Health"
    ],
    "Montage": [
        "Future of Work"
    ],
    "InContext Solutions": [
        "Data & Analytics",
        "Deeptech / Robotics / AR/VR"
    ],
    "Peerius": [
        "Consumer",
        "Data & Analytics"
    ],
    "Chargemaster": [
        "Transportation / Mobility",
        "Climate / Sustainability"
    ],
    "Big Data Partnership": [
        "Data & Analytics"
    ],
    "Pipp Mobile": [
        "Logistics / Supply Chain"
    ],
    "Fiber By-Products": [
        "Climate / Sustainability"
    ],
    "Young Innovations": [
        "Health"
    ],
    "mophie": [
        "Consumer"
    ],
    "Vigilant Applications": [
        "Cybersecurity",
        "Data & Analytics"
    ],
    "Third Bridge": [
        "FinTech / Insurance",
        "Data & Analytics"
    ],
    "Campden Wealth": [
        "FinTech / Insurance"
    ],
    "Conversity": [
        "Data & Analytics"
    ],
    "SenseLogix": [
        "Climate / Sustainability",
        "PropTech"
    ],
    "APM Healthcare": [
        "Health"
    ],
    "MatsSoft": [
        "Future of Work",
        "Dev Tools / Cloud"
    ],
    "Sakti3": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Xanitos": [
        "Health"
    ],
    "Delphinus": [
        "Health"
    ],
    "Freeosk": [
        "Consumer",
        "CPG"
    ],
    "RevSpring": [
        "FinTech / Insurance",
        "Health"
    ],
    "SPC International": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Utility Exchange Online": [
        "Climate / Sustainability"
    ],
    "UICO": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Chess Dynamics": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Saffron Digital": [
        "Gaming / Media / Entertainment"
    ],
    "Cogora": [
        "Gaming / Media / Entertainment",
        "Health"
    ],
    "dianomi": [
        "Gaming / Media / Entertainment",
        "FinTech / Insurance"
    ],
    "Mergermarket": [
        "FinTech / Insurance",
        "Data & Analytics"
    ],
    "Celebrus Technologies": [
        "Data & Analytics"
    ],
    "Fjord": [
        "Gaming / Media / Entertainment"
    ],
    "Espresso Education": [
        "Future of Work",
        "Gaming / Media / Entertainment"
    ],
    "Lupa Foods": [
        "CPG"
    ],
    "Ranir": [
        "CPG",
        "Health"
    ],
    "Hygenica": [
        "Health"
    ],
    "Abzena": [
        "BioTech",
        "Health"
    ],
    "Akadeum Life Sciences": [
        "BioTech",
        "Health"
    ],
    "Genomenon": [
        "BioTech",
        "Health"
    ],
    "Trapelo Health": [
        "Health",
        "Data & Analytics"
    ],
    "Population Genetics": [
        "BioTech",
        "Health"
    ],
    "Gas Station TV": [
        "Gaming / Media / Entertainment"
    ],
    "Blis": [
        "Gaming / Media / Entertainment",
        "Data & Analytics"
    ],
    "ResponseTap": [
        "Data & Analytics"
    ],
    "Celoxica": [
        "FinTech / Insurance"
    ],
    "EDITED": [
        "Data & Analytics",
        "Consumer"
    ],
    "Second Nature": [
        "Health",
        "Consumer"
    ],
    "Thread": [
        "Consumer"
    ],
    "Watchfinder & Co.": [
        "Consumer"
    ],
    "MyOptique Group": [
        "Consumer",
        "Health"
    ],
    "StorePower": [
        "CPG",
        "Consumer"
    ],
    "Archdesk": [
        "PropTech"
    ],
    "InvestNext": [
        "PropTech",
        "FinTech / Insurance"
    ],
    "Exonar": [
        "Data & Analytics",
        "Cybersecurity"
    ],
    "Cipher": [
        "Data & Analytics",
        "RegTech/Gov/Legal"
    ],
    "Doctify": [
        "Health",
        "Consumer"
    ],
    "Sovato Health": [
        "Health",
        "Deeptech / Robotics / AR/VR"
    ],
}


def find_investments(o):
    if isinstance(o, dict):
        if isinstance(o.get("investments"), list):
            return o["investments"]
        for v in o.values():
            r = find_investments(v)
            if r:
                return r
    elif isinstance(o, list):
        for v in o:
            r = find_investments(v)
            if r:
                return r
    return None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("FATAL: __NEXT_DATA__ not found")
    inv = find_investments(json.loads(m.group(1))) or []
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for x in inv:
        name = clean(x.get("company"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(x.get("strapline"))
        sectors = [clean(s.get("title")) for s in (x.get("sectors") or []) if isinstance(s, dict) and clean(s.get("title"))]
        raw = clean(x.get("status"))
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(x.get("link")),
            "status": STATUS.get((raw or "").lower()),
            "site_status": raw,
            "fund": FUND.get(x.get("fund"), x.get("fund")),
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
