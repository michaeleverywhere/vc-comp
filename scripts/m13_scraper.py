#!/usr/bin/env python3
"""M13 portfolio scraper -> m13_companies.json
Source: https://www.m13.co/portfolio — Webflow CMS list (server-rendered,
`?ac686a15_page=N` pagination followed). Each row carries the company name,
a one-line description and hidden Finsweet fields: sector, status
(Current / Exited) and category = M13's initial investment round
(Pre-Seed / Seed / Series A ...). The row opens a JS popup only, so no
company website, location or year is published on-page.
Initial investment round -> stage. Status: Current -> active; Exited ->
acquired (raw kept in site_status).
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, tags_for, stage_label, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.m13.co/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "m13_companies.json")
PRIMARY = "M13"
STATUS = {"current": "active", "active": "active", "exited": "acquired", "acquired": "acquired"}
SECTOR_TAG_MAP = {
    "healthcare": ["Health"], "health": ["Health"], "fintech": ["FinTech / Insurance"], "consumer": ["Consumer"],
    "climate": ["Climate / Sustainability"], "sustainability": ["Climate / Sustainability"],
    "commerce": ["Consumer"], "future of work": ["Future of Work"], "mobility": ["Transportation / Mobility"],
    "supply chain": ["Logistics / Supply Chain"], "logistics": ["Logistics / Supply Chain"],
    "real estate": ["PropTech"], "proptech": ["PropTech"], "media": ["Gaming / Media / Entertainment"],
    "gaming": ["Gaming / Media / Entertainment"], "web3": ["Web3 / Crypto"], "crypto": ["Web3 / Crypto"],
    "security": ["Cybersecurity"], "cybersecurity": ["Cybersecurity"],
    "blockchain": ["Web3 / Crypto"], "govtech": ["RegTech/Gov/Legal"], "climate/energy": ["Climate / Sustainability"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Allocate": [
        "FinTech / Insurance"
    ],
    "Ambrus Studio": [
        "Gaming / Media / Entertainment",
        "Web3 / Crypto"
    ],
    "Ancient Nutrition": [
        "CPG",
        "Health"
    ],
    "Anycart": [
        "Consumer",
        "CPG"
    ],
    "Anything": [
        "Dev Tools / Cloud"
    ],
    "Arena Club": [
        "Consumer"
    ],
    "Avantos AI": [
        "FinTech / Insurance",
        "Future of Work"
    ],
    "AvatarOS": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "AxleAuto": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Ayble Health": [
        "Health"
    ],
    "Banyan": [
        "Data & Analytics",
        "FinTech / Insurance"
    ],
    "Baselayer": [
        "Cybersecurity",
        "FinTech / Insurance"
    ],
    "Bento": [
        "Health",
        "Consumer"
    ],
    "Betty Labs": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Big Whale Labs": [
        "Web3 / Crypto",
        "FinTech / Insurance"
    ],
    "Bounty": [
        "Gaming / Media / Entertainment"
    ],
    "Briefcase": [
        "FinTech / Insurance"
    ],
    "Cabify": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Carbon 38": [
        "Consumer"
    ],
    "CAT Labs": [
        "Web3 / Crypto",
        "Cybersecurity",
        "RegTech/Gov/Legal"
    ],
    "Chomps": [
        "CPG"
    ],
    "Chord": [
        "Data & Analytics",
        "Consumer"
    ],
    "Composer": [
        "FinTech / Insurance"
    ],
    "CreatorDAO": [
        "Gaming / Media / Entertainment",
        "Web3 / Crypto"
    ],
    "Daily Harvest": [
        "CPG",
        "Consumer"
    ],
    "Daylight Energy": [
        "Climate / Sustainability",
        "Web3 / Crypto"
    ],
    "Delphia": [
        "Data & Analytics",
        "RegTech/Gov/Legal"
    ],
    "Digiphy": [
        "Consumer"
    ],
    "Doorstead": [
        "PropTech"
    ],
    "Doorvest": [
        "PropTech",
        "FinTech / Insurance"
    ],
    "Dot.LA": [
        "Gaming / Media / Entertainment"
    ],
    "Dupe": [
        "Consumer"
    ],
    "Emerge Now": [
        "Deeptech / Robotics / AR/VR",
        "Consumer"
    ],
    "Ensemble AI": [
        "Dev Tools / Cloud"
    ],
    "Estuary": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
    "Fable": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "Flexspace AI": [
        "PropTech",
        "Future of Work"
    ],
    "Flipside": [
        "Web3 / Crypto",
        "Data & Analytics"
    ],
    "Forevernote": [
        "Consumer"
    ],
    "FSL": [
        "Web3 / Crypto",
        "Consumer"
    ],
    "Green Zuru": [
        "Climate / Sustainability",
        "PropTech"
    ],
    "Hark": [
        "Data & Analytics",
        "Consumer"
    ],
    "Hey, Walt!": [
        "PropTech"
    ],
    "Hivemapper": [
        "Web3 / Crypto",
        "Data & Analytics"
    ],
    "Homelister": [
        "PropTech"
    ],
    "Honest Day's Work": [
        "Future of Work"
    ],
    "Huddles": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Humata": [
        "Future of Work"
    ],
    "Influential": [
        "Gaming / Media / Entertainment"
    ],
    "interviewing.io": [
        "Future of Work"
    ],
    "Io.net": [
        "Web3 / Crypto",
        "Dev Tools / Cloud"
    ],
    "Jackpocket": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "Joydays": [
        "CPG"
    ],
    "Karate Combat": [
        "Gaming / Media / Entertainment",
        "Web3 / Crypto"
    ],
    "KeVita": [
        "CPG"
    ],
    "Kindra": [
        "Health",
        "CPG"
    ],
    "Kino": [
        "Gaming / Media / Entertainment"
    ],
    "Kontext": [
        "Gaming / Media / Entertainment",
        "Dev Tools / Cloud"
    ],
    "Koodos": [
        "Dev Tools / Cloud",
        "Consumer"
    ],
    "Lantern": [
        "Future of Work"
    ],
    "Layla Ai": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Lightning Labs": [
        "Web3 / Crypto",
        "Dev Tools / Cloud"
    ],
    "Locker Room": [
        "Gaming / Media / Entertainment"
    ],
    "LOU": [
        "Future of Work",
        "Dev Tools / Cloud"
    ],
    "Luminos": [
        "RegTech/Gov/Legal"
    ],
    "Lyft": [
        "Transportation / Mobility"
    ],
    "MAKORA": [
        "Dev Tools / Cloud"
    ],
    "Mantle": [
        "FinTech / Insurance",
        "Data & Analytics"
    ],
    "Matterport": [
        "Deeptech / Robotics / AR/VR",
        "PropTech"
    ],
    "Maven": [
        "Future of Work"
    ],
    "Max Retail": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "Mento": [
        "Future of Work"
    ],
    "Milo": [
        "FinTech / Insurance",
        "Web3 / Crypto",
        "PropTech"
    ],
    "Mosaic": [
        "Consumer",
        "Future of Work"
    ],
    "Mud/Wtr": [
        "CPG"
    ],
    "Niural": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "Northstar": [
        "FinTech / Insurance",
        "Future of Work"
    ],
    "OpenFX": [
        "FinTech / Insurance"
    ],
    "Opus": [
        "Health"
    ],
    "Packsmith": [
        "Logistics / Supply Chain"
    ],
    "Passport": [
        "Logistics / Supply Chain",
        "Consumer"
    ],
    "Pietra": [
        "Consumer",
        "CPG"
    ],
    "PIKL": [
        "Future of Work"
    ],
    "Pinata": [
        "Future of Work"
    ],
    "Pinterest": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "Play": [
        "Dev Tools / Cloud"
    ],
    "Play Money Studios": [
        "FinTech / Insurance"
    ],
    "Podz": [
        "Gaming / Media / Entertainment"
    ],
    "Popshop": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "Prepared": [
        "RegTech/Gov/Legal"
    ],
    "ProGuides": [
        "Gaming / Media / Entertainment"
    ],
    "Project Aeon": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "Quill": [
        "RegTech/Gov/Legal"
    ],
    "Replenysh": [
        "Climate / Sustainability"
    ],
    "Rime": [
        "Dev Tools / Cloud"
    ],
    "Ring": [
        "Consumer",
        "Cybersecurity"
    ],
    "Robyn AI": [
        "Health",
        "Consumer"
    ],
    "Rock the Bells": [
        "Gaming / Media / Entertainment"
    ],
    "Rothy's": [
        "Consumer"
    ],
    "Saga.xyz": [
        "Web3 / Crypto",
        "Gaming / Media / Entertainment"
    ],
    "Scopely": [
        "Gaming / Media / Entertainment"
    ],
    "Score Travel": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Seed Health": [
        "Health",
        "CPG"
    ],
    "SellOut": [
        "Consumer"
    ],
    "Shake Shack": [
        "Consumer"
    ],
    "Shef": [
        "Consumer"
    ],
    "Sitch": [
        "Consumer"
    ],
    "Skyfall AI": [
        "Dev Tools / Cloud"
    ],
    "SMS Assist": [
        "PropTech"
    ],
    "Social Native": [
        "Gaming / Media / Entertainment"
    ],
    "Soothe": [
        "Consumer",
        "Health"
    ],
    "Source": [
        "PropTech",
        "Logistics / Supply Chain"
    ],
    "SpaceX": [
        "Deeptech / Robotics / AR/VR",
        "Transportation / Mobility"
    ],
    "Superlocal": [
        "Consumer"
    ],
    "Superscript": [
        "Health"
    ],
    "Tamber": [
        "Gaming / Media / Entertainment"
    ],
    "Tarform": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Tecovas": [
        "Consumer"
    ],
    "Teleskope": [
        "Cybersecurity",
        "Data & Analytics"
    ],
    "The Bouqs Company": [
        "Consumer"
    ],
    "Thrive Global": [
        "Health",
        "Future of Work"
    ],
    "Thrive Market": [
        "Consumer",
        "CPG"
    ],
    "Toki Commerce": [
        "Consumer"
    ],
    "Tonal": [
        "Health",
        "Consumer"
    ],
    "Transfix": [
        "Logistics / Supply Chain"
    ],
    "Umamicart": [
        "Consumer",
        "CPG"
    ],
    "Unblocked": [
        "Gaming / Media / Entertainment",
        "Web3 / Crypto"
    ],
    "Upwards": [
        "Consumer",
        "Future of Work"
    ],
    "Vambe AI": [
        "Future of Work"
    ],
    "Visor": [
        "Future of Work"
    ],
    "Voice.ai": [
        "Gaming / Media / Entertainment",
        "Dev Tools / Cloud"
    ],
    "VoyceMe": [
        "Gaming / Media / Entertainment"
    ],
    "Wellthy": [
        "Health",
        "Future of Work"
    ],
    "WorkMade": [
        "FinTech / Insurance"
    ],
    "Zelo": [
        "Future of Work",
        "RegTech/Gov/Legal"
    ],
    "Zenlytic": [
        "Data & Analytics"
    ],
    "Detect": [
        "Health"
    ],
    "Capsule": [
        "Health"
    ],
    "Classpass": [
        "Consumer",
        "Health"
    ],
    "Headspace": [
        "Health",
        "Consumer"
    ],
    "Next Health": [
        "Health"
    ],
    "Lifeforce": [
        "Health"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select("div.c-port-item.w-dyn-item"):
            h = it.select_one('[fs-list-field="name"]')
            name = clean(h.get_text(" ")) if h else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            sub = it.select_one(".c-port-sub")
            desc = clean(sub.get_text(" ")) if sub else None
            f = lambda k: [clean(x.get_text(" ")) for x in it.select(f'.u-hide [fs-list-field="{k}"]') if clean(x.get_text(" "))]
            sectors = f("sector")
            status = (f("status") or [None])[0]
            rounds = f("category")
            out.append({
                "company_name": name,
                "description": desc,
                "status": STATUS.get((status or "").lower()),
                "site_status": status,
                "stage": stage_label(rounds[0]) if rounds else None,
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
    for k in ("description", "status", "stage", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
