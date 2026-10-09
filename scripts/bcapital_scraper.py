#!/usr/bin/env python3
"""B Capital portfolio scraper -> bcapital_companies.json
Source: https://b.capital/portfolio — WordPress page that embeds the full
portfolio as a JS array (`orig_data = [...]`) used by the card popups. Each
entry has title, one-line description (txt), region (tagplace), status
(Active / Exited), industry group (Technology & AI / Healthcare / Energy /
Opportunistic) and the company's website (link_href).
Region -> location (the site's own geography label). Exited -> acquired
(raw label kept in site_status). No rounds or dates are published, so stage /
first_invested stay blank.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://b.capital/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "bcapital_companies.json")
PRIMARY = "B Capital"
STATUS = {"active": "active", "exited": "acquired"}
SECTOR_TAG_MAP = {
    "healthcare": ["Health"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "1AU": [
        "Deeptech / Robotics / AR/VR"
    ],
    "6sense": [
        "Data & Analytics",
        "Future of Work"
    ],
    "Accacia": [
        "Climate / Sustainability",
        "PropTech",
        "Data & Analytics"
    ],
    "Apptronik": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Axiom": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Baichuan": [
        "Dev Tools / Cloud"
    ],
    "BuildOps": [
        "Future of Work",
        "PropTech"
    ],
    "Certn": [
        "Cybersecurity",
        "Future of Work"
    ],
    "ChipAgents": [
        "Deeptech / Robotics / AR/VR",
        "Dev Tools / Cloud"
    ],
    "CompanyCam": [
        "Future of Work",
        "PropTech"
    ],
    "Curbwaste": [
        "Climate / Sustainability",
        "Future of Work"
    ],
    "Dream Labs": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Extend": [
        "FinTech / Insurance"
    ],
    "Fervo Energy": [
        "Climate / Sustainability"
    ],
    "FlowGPT": [
        "Consumer",
        "Dev Tools / Cloud"
    ],
    "Forest": [],
    "Gable": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Goose": [
        "Future of Work",
        "Consumer"
    ],
    "Grace Investment Machine": [
        "FinTech / Insurance"
    ],
    "Gushwork": [
        "Future of Work"
    ],
    "HavocAI": [
        "Deeptech / Robotics / AR/VR",
        "Transportation / Mobility"
    ],
    "HotSpot Therapeutics": [
        "Health",
        "BioTech"
    ],
    "Hypersonix": [
        "Data & Analytics",
        "Consumer"
    ],
    "Icertis": [
        "RegTech/Gov/Legal",
        "Future of Work"
    ],
    "InfraHub": [
        "Transportation / Mobility",
        "Data & Analytics"
    ],
    "Kopi Kenangan": [
        "Consumer",
        "CPG"
    ],
    "Labelbox": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Labviva": [
        "BioTech",
        "Logistics / Supply Chain"
    ],
    "Lambda": [
        "Dev Tools / Cloud"
    ],
    "LevelTen": [
        "Climate / Sustainability"
    ],
    "Lively": [
        "Health",
        "FinTech / Insurance"
    ],
    "Neushen Therapeutics": [
        "Health",
        "BioTech"
    ],
    "Odeko": [
        "Logistics / Supply Chain",
        "Consumer"
    ],
    "Percent": [
        "FinTech / Insurance"
    ],
    "Perplexity": [
        "Consumer",
        "Dev Tools / Cloud"
    ],
    "Poolside": [
        "Dev Tools / Cloud"
    ],
    "Precision Neuro": [
        "Health",
        "Deeptech / Robotics / AR/VR"
    ],
    "Solar Square": [
        "Climate / Sustainability",
        "PropTech"
    ],
    "Karman Industries": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "TinyHealth": [
        "Health",
        "BioTech"
    ],
    "Yalo": [
        "Consumer",
        "Future of Work"
    ],
    "Zaihui": [
        "Consumer",
        "Future of Work"
    ],
    "Turno": [
        "Transportation / Mobility",
        "FinTech / Insurance",
        "Climate / Sustainability"
    ],
    "Star Catcher": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "JetZero": [
        "Transportation / Mobility",
        "Climate / Sustainability"
    ],
    "Innovaccer": [
        "Health",
        "Data & Analytics"
    ],
    "Fountain": [
        "Future of Work"
    ],
    "Remote": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "EvenUp": [
        "RegTech/Gov/Legal"
    ],
    "Brik": [
        "PropTech",
        "Logistics / Supply Chain"
    ],
    "Nest Genomics": [
        "Health",
        "BioTech"
    ],
    "MediTrust": [
        "Health",
        "FinTech / Insurance"
    ],
    "Unblocked Brands": [
        "Web3 / Crypto",
        "Consumer"
    ],
    "Floor NFTs": [
        "Web3 / Crypto",
        "Consumer"
    ],
    "Sonilo": [
        "Gaming / Media / Entertainment"
    ],
    "Bhanzu": [
        "Consumer"
    ],
    "Inspace": [
        "PropTech"
    ],
    "Iru": [
        "Cybersecurity",
        "Dev Tools / Cloud"
    ],
    "Writer": [
        "Dev Tools / Cloud",
        "Future of Work"
    ],
    "Reflection": [
        "Dev Tools / Cloud"
    ],
    "Seltz": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
    "Goodfire": [
        "Dev Tools / Cloud"
    ],
    "PaleBlueDot": [
        "Dev Tools / Cloud"
    ],
    "Code Metal": [
        "Dev Tools / Cloud"
    ],
    "Collinear AI": [
        "Dev Tools / Cloud"
    ],
    "Knox": [
        "Cybersecurity",
        "RegTech/Gov/Legal"
    ],
    "Fortanix": [
        "Cybersecurity"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    m = re.search(r"orig_data\s*=\s*(\[.*?\]);", html, re.S)
    if not m:
        sys.exit("orig_data array not found")
    data = json.loads(m.group(1))
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for d in data:
        name = clean(d.get("title"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(d.get("txt"))
        sectors = [s for s in [clean(d.get("industry"))] if s]
        raw_status = clean(d.get("tagstate"))
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(d.get("link_href")) if d.get("link_href") else None,
            "company_profile_url": urljoin(SOURCE_URL, d["permalink"]) if d.get("permalink") else None,
            "status": STATUS.get((raw_status or "").lower()),
            "site_status": raw_status,
            "location": clean(d.get("tagplace")),
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc or "", sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "location", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
