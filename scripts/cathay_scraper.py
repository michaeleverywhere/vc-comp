#!/usr/bin/env python3
"""Cathay Innovation portfolio scraper -> cathay_companies.json
Source: https://cathayinnovation.com/portfolio/ — WordPress page whose grid
cards (`div.co-card`) carry every field as data-attributes: data-name,
data-description (HTML), data-round-type (round Cathay entered at), data-fund,
data-year (year of Cathay's investment), data-exit ("Acquired: X" or a
listing such as "NASDAQ: CHYM"), data-link (company website), data-read-more.
stage = data-round-type (entry round). "Acquired: X" -> status acquired +
acquirer; a ticker -> ipo_listing (status left blank: site doesn't say active).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, html_text, tags_for, clean_url, year_of, stage_label, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://cathayinnovation.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "cathay_companies.json")
PRIMARY = "Cathay Innovation"
SECTOR_TAG_MAP = {}
# Hand-reviewed tag fixes (judgment pass, no LLM).
TAG_OVERRIDES = {
    "Alma": [
        "FinTech / Insurance",
        "Consumer"
    ],
    "FirstVet": [
        "Health",
        "Consumer"
    ],
    "Aerobotics": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "KaiOS Technologies": [
        "Consumer",
        "Dev Tools / Cloud"
    ],
    "Datasine": [
        "Data & Analytics"
    ],
    "AnotherBrain": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Cosmo Tech": [
        "Data & Analytics"
    ],
    "Skan.ai": [
        "Future of Work",
        "Data & Analytics"
    ],
    "AI Rudder": [
        "Future of Work"
    ],
    "Chatail": [
        "Consumer",
        "Future of Work"
    ],
    "Entalpic": [
        "Deeptech / Robotics / AR/VR",
        "Climate / Sustainability"
    ],
    "MGX (Deep Wisdom)": [
        "Dev Tools / Cloud"
    ],
    "GoMyCode": [
        "Future of Work",
        "Consumer"
    ],
    "Henry": [
        "Future of Work",
        "Consumer"
    ],
    "AMI Labs": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Moonshot AI (Kimi)": [
        "Dev Tools / Cloud",
        "Consumer"
    ],
    "Drivy": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Paycar": [
        "FinTech / Insurance",
        "Transportation / Mobility"
    ],
    "Peek": [
        "Consumer"
    ],
    "Glovo": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "Nabla": [
        "Health"
    ],
    "Beatbot": [
        "Consumer",
        "Deeptech / Robotics / AR/VR"
    ],
    "Nile AG": [
        "Logistics / Supply Chain",
        "Climate / Sustainability"
    ],
    "Ledger": [
        "Web3 / Crypto",
        "Cybersecurity"
    ],
    "Mogic": [
        "Gaming / Media / Entertainment",
        "Future of Work"
    ],
    "Tuhu": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Cloudpick": [
        "Consumer",
        "Deeptech / Robotics / AR/VR"
    ],
    "Galaxea": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Qualified Health": [
        "Health"
    ],
    "Tucuvi": [
        "Health"
    ],
    "Resilience": [
        "Health",
        "Data & Analytics"
    ],
    "Laiye Technology": [
        "Future of Work"
    ],
    "Upway": [
        "Transportation / Mobility",
        "Consumer",
        "Climate / Sustainability"
    ]
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for c in soup.select("div.co-card[data-name]"):
        name = clean(c.get("data-name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = html_text(c.get("data-description") or "")
        ex = clean(c.get("data-exit"))
        acquirer, listing = None, None
        if ex:
            m = re.match(r"(?i)acquired\s*(?:by)?\s*:?\s*(.+)$", ex)
            if m:
                acquirer = clean(m.group(1))
            elif ":" in ex:
                listing = ex
        rnd = clean(c.get("data-round-type"))
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(c.get("data-link")),
            "entry_round": rnd,
            "stage": stage_label(rnd),
            "fund": clean(c.get("data-fund")),
            "first_invested": year_of(c.get("data-year")),
            "exit": ex,
            "acquirer": acquirer,
            "ipo_listing": listing,
            "status": "acquired" if acquirer else None,
            "read_more_url": clean(c.get("data-read-more")),
            "everywhere_tags": tags_for(name, desc, [], SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "stage", "first_invested", "status", "ipo_listing", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
