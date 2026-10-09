#!/usr/bin/env python3
"""Industrifonden portfolio scraper -> industrifonden_companies.json
Source: https://industrifonden.com/portfolio — Webflow CMS accordion list,
fully server-rendered. Each item has the name, a tagline, a long
description and an info card with STATUS (Active / Selected exits),
AREA (Industrifonden's investment area: Life science / Software /
Deep tech & planetary health / Growth), WEBSITE and the partner contact.
No stage, location or year is published.
Status: Active -> active; Selected exits -> acquired (raw kept in site_status).
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://industrifonden.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "industrifonden_companies.json")
PRIMARY = "Industrifonden"
STATUS = {"active": "active", "selected exits": "acquired"}
SECTOR_TAG_MAP = {"life science": ["BioTech", "Health"]}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Accedo": [
        "Gaming / Media / Entertainment",
        "Dev Tools / Cloud"
    ],
    "AdamantQ": [
        "Deeptech / Robotics / AR/VR"
    ],
    "AlixLabs": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Apica": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
    "Arcam": [
        "Deeptech / Robotics / AR/VR",
        "Health"
    ],
    "Arevo": [
        "Climate / Sustainability",
        "CPG"
    ],
    "Avidicare": [
        "Health"
    ],
    "BrainZell": [
        "BioTech",
        "Health"
    ],
    "Cascade Drives": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "CellaVision": [
        "Health",
        "BioTech"
    ],
    "Cellevate": [
        "BioTech"
    ],
    "Digip": [
        "RegTech/Gov/Legal"
    ],
    "eBuilder": [
        "Cybersecurity"
    ],
    "Echandia": [
        "Climate / Sustainability",
        "Transportation / Mobility"
    ],
    "Enginio": [
        "Consumer",
        "Data & Analytics"
    ],
    "Enginzyme": [
        "BioTech",
        "Climate / Sustainability"
    ],
    "Envirotainer": [
        "Logistics / Supply Chain",
        "Health"
    ],
    "Evam": [
        "Dev Tools / Cloud",
        "Health"
    ],
    "Exeri": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Fast Travel Games": [
        "Gaming / Media / Entertainment",
        "Deeptech / Robotics / AR/VR"
    ],
    "Fibbl": [
        "Consumer",
        "Deeptech / Robotics / AR/VR"
    ],
    "Fishbrain": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "Footway Oaas": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "Freemelt": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Gårdsfisk": [
        "CPG",
        "Climate / Sustainability"
    ],
    "Inriver": [
        "Data & Analytics",
        "Consumer"
    ],
    "KISAB": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Limina": [
        "FinTech / Insurance",
        "Future of Work"
    ],
    "Melt&Marble": [
        "CPG",
        "BioTech",
        "Climate / Sustainability"
    ],
    "Micvac": [
        "CPG"
    ],
    "Minervax": [
        "BioTech",
        "Health"
    ],
    "Movimento": [
        "Transportation / Mobility",
        "Dev Tools / Cloud"
    ],
    "Nextory": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Nodica Group": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Novatron": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Nuvoair": [
        "Health"
    ],
    "Oatly": [
        "CPG",
        "Climate / Sustainability"
    ],
    "Occtoo": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Photon Sports": [
        "Health",
        "Consumer"
    ],
    "Realforce": [
        "PropTech"
    ],
    "Retein": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Roots Bio": [
        "BioTech",
        "Climate / Sustainability"
    ],
    "SaltX": [
        "Climate / Sustainability"
    ],
    "Scalado": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "SeaPattern": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Soundtrack Technologies": [
        "Gaming / Media / Entertainment"
    ],
    "Soundtrap": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Texray": [
        "Health",
        "Deeptech / Robotics / AR/VR"
    ],
    "TrackPaw": [
        "BioTech",
        "Health"
    ],
    "Trialbee": [
        "Health",
        "BioTech"
    ],
    "TrusTrace": [
        "Logistics / Supply Chain",
        "Climate / Sustainability",
        "Consumer"
    ],
    "Valdyr (Telness Tech)": [
        "Dev Tools / Cloud"
    ],
    "Vesiro": [
        "Dev Tools / Cloud",
        "Climate / Sustainability"
    ],
    "Viking analytics": [
        "Data & Analytics",
        "Deeptech / Robotics / AR/VR"
    ],
    "Yangi": [
        "Climate / Sustainability",
        "CPG"
    ],
    "ZeroPoint": [
        "Deeptech / Robotics / AR/VR",
        "Dev Tools / Cloud",
        "Climate / Sustainability"
    ],
    "Zymego": [
        "Health"
    ],
    "Airsonett": [
        "Health"
    ],
    "AMRA": [
        "Health",
        "Data & Analytics"
    ],
    "Bioinvent": [
        "BioTech",
        "Health"
    ],
    "Nuevolution": [
        "BioTech",
        "Health"
    ],
    "Funnel": [
        "Data & Analytics"
    ],
    "Hopsworks": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select("div.accordion-item.w-dyn-item"):
        h = it.select_one(".accordion-trigger .headline-sans-m")
        name = clean(h.get_text(" ")) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        tg = it.select_one(".accordion-trigger .headline-serif-m")
        tagline = clean(tg.get_text(" ")) if tg else None
        d = it.select_one(".accordion-content .body-m")
        desc = clean(d.get_text(" ")) if d else None
        info, site = {}, None
        for f in it.select(".portfolio-inof_card .flex-h-span"):
            k = f.select_one(".headline-sans-xs")
            if not k:
                continue
            key = clean(k.get_text(" ")).lower()
            vals = list(f.stripped_strings)[1:]
            info[key] = clean(" ".join(vals))
            if key == "website":
                a = f.select_one("a[href]")
                site = a["href"] if a else None
        area = info.get("area")
        sectors = [area] if area else []
        raw = info.get("status")
        out.append({
            "company_name": name,
            "description": desc or tagline,
            "tagline": tagline,
            "company_url": clean_url(site),
            "status": STATUS.get((raw or "").lower()),
            "site_status": raw,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, " ".join(x for x in (tagline, desc) if x), sectors, SECTOR_TAG_MAP),
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
