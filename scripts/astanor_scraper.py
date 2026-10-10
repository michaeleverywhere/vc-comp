#!/usr/bin/env python3
"""Astanor portfolio scraper -> astanor_companies.json
Source: https://astanor.com/portfolio/ — WordPress (Avada post cards). Each card
links to /entrepreneurs/<slug>/ and shows name, Astanor's investment stage
(Seed / Venture / Growth) and a one-line tagline. Detail pages add Company
Name, Location (region, country, city), Impact KPIs, Investment Stage, the
company website ("Visit website") and a long-form description.
stage = Investment Stage only when it is a funding round (Seed); "Venture" /
"Growth" are Astanor fund buckets, kept verbatim in investment_stage.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, stage_label, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://astanor.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "astanor_companies.json")
PRIMARY = "Astanor"
SECTOR_TAG_MAP = {}
LABELS = ("Company Name :", "Location :", "Impact KPIs :", "Investment Stage :", "Visit website")
# Hand-reviewed tag fixes (judgment pass, no LLM): Astanor is an agrifood/bioeconomy fund,
# so long-form copy over-triggers keyword tags; every company reviewed by name + tagline.
TAG_OVERRIDES = {
    "4ag": [
        "Deeptech / Robotics / AR/VR",
        "Climate / Sustainability"
    ],
    "Aardaia": [
        "BioTech",
        "Climate / Sustainability"
    ],
    "AgZen": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Akson Robotics": [
        "Deeptech / Robotics / AR/VR",
        "Climate / Sustainability"
    ],
    "Amplifye": [
        "BioTech",
        "Health",
        "CPG"
    ],
    "Apeel": [
        "Climate / Sustainability",
        "CPG",
        "Logistics / Supply Chain"
    ],
    "Aphea Bio": [
        "BioTech",
        "Climate / Sustainability"
    ],
    "Bettafish": [
        "CPG",
        "Climate / Sustainability"
    ],
    "Biofluff": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Biomatter": [
        "BioTech",
        "Climate / Sustainability"
    ],
    "Calice": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Calyxia": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Consensus Foods": [
        "CPG",
        "Data & Analytics"
    ],
    "CrowdFarming": [
        "Consumer",
        "CPG",
        "Climate / Sustainability"
    ],
    "Culinary Sciences": [
        "CPG",
        "Deeptech / Robotics / AR/VR"
    ],
    "Florey Biosciences": [
        "BioTech",
        "Health"
    ],
    "Galley": [
        "Dev Tools / Cloud",
        "CPG"
    ],
    "Heali AI": [
        "Health",
        "Consumer"
    ],
    "Helyx Industries": [
        "BioTech",
        "Health"
    ],
    "Hijack Bio": [
        "BioTech",
        "Health"
    ],
    "Holobiome": [
        "BioTech",
        "Health"
    ],
    "HowGood": [
        "Data & Analytics",
        "Climate / Sustainability",
        "CPG"
    ],
    "Hungry Marketplace": [
        "Consumer",
        "Future of Work"
    ],
    "IN TRUTH": [
        "Health",
        "Data & Analytics"
    ],
    "iUNU": [
        "Climate / Sustainability",
        "Data & Analytics",
        "Deeptech / Robotics / AR/VR"
    ],
    "La Fourche": [
        "Consumer",
        "CPG"
    ],
    "LiveCycle": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Magrowtec": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Matrix Pack": [
        "Climate / Sustainability",
        "CPG"
    ],
    "Meet My Mama": [
        "Future of Work",
        "Consumer"
    ],
    "Metabolic Psychiatry Labs": [
        "Health"
    ],
    "Metabolize": [
        "Health"
    ],
    "Micro Harvest": [
        "BioTech",
        "Climate / Sustainability"
    ],
    "Miimosa": [
        "FinTech / Insurance",
        "Climate / Sustainability"
    ],
    "MiTerro": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Modern Meadow": [
        "BioTech",
        "Climate / Sustainability"
    ],
    "Monarch": [
        "Deeptech / Robotics / AR/VR",
        "Climate / Sustainability"
    ],
    "Notpla": [
        "Climate / Sustainability",
        "CPG"
    ],
    "Olombria": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "Omeza": [
        "Health",
        "BioTech"
    ],
    "Planetary": [
        "BioTech",
        "Climate / Sustainability"
    ],
    "Plantible": [
        "CPG",
        "Climate / Sustainability",
        "BioTech"
    ],
    "Produce Pay": [
        "FinTech / Insurance",
        "Logistics / Supply Chain"
    ],
    "Reshape": [
        "BioTech",
        "Deeptech / Robotics / AR/VR"
    ],
    "RFI Ingredients": [
        "CPG",
        "Health"
    ],
    "Robovision": [
        "Deeptech / Robotics / AR/VR",
        "Dev Tools / Cloud"
    ],
    "Source Ag": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Spectacular Labs": [
        "BioTech",
        "CPG"
    ],
    "Standing Ovation": [
        "BioTech",
        "CPG",
        "Climate / Sustainability"
    ],
    "Swap": [
        "CPG",
        "Climate / Sustainability"
    ],
    "Switch Bioworks": [
        "BioTech",
        "Climate / Sustainability"
    ],
    "The Gut Stuff": [
        "Health",
        "CPG",
        "Consumer"
    ],
    "Tractor Junction": [
        "Consumer",
        "Transportation / Mobility"
    ],
    "Unlocked Labs": [
        "BioTech",
        "Health"
    ],
    "v2Food": [
        "CPG",
        "Climate / Sustainability"
    ],
    "Vivent Biosignals": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Zya": [
        "Health",
        "BioTech"
    ]
}


def detail(html):
    d = BeautifulSoup(html, "html.parser")
    strings = [clean(s) for s in d.stripped_strings]
    strings = [s for s in strings if s]
    f, cur = {}, None
    for s in strings:
        if s in LABELS:
            cur = s
            if s == "Visit website":
                break
            f[cur] = []
            continue
        if cur:
            f[cur].append(s)
    site = next((a["href"] for a in d.select("a[href^=http]") if clean(a.get_text(" ")) == "Visit website"), None)
    texts = [clean(t.get_text(" ")) for t in d.select(".fusion-text")]
    texts = [t for t in texts if t and len(t) > 80]
    desc = max(texts, key=len) if texts else None
    loc = [x.rstrip(",").strip() for x in f.get("Location :", []) if x.rstrip(",").strip()]
    return {
        "name": (f.get("Company Name :") or [None])[0],
        "location_parts": loc,
        "impact_kpis": [x.strip() for x in " ".join(f.get("Impact KPIs :", [])).split(",") if x.strip()],
        "investment_stage": (f.get("Investment Stage :") or [None])[0],
        "site": site,
        "desc": desc,
    }


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards, seen = [], set()
    for li in soup.select("li.post-card"):
        a = li.select_one("a[href*='/entrepreneurs/']")
        if not a or a["href"] in seen:
            continue
        seen.add(a["href"])
        strs = [clean(s) for s in li.stripped_strings if clean(s)]
        cards.append((a["href"], strs))
    if limit:
        cards = cards[:limit]
    pages = fetch_many([h for h, _ in cards], workers=6)
    out = []
    for href, strs in cards:
        info = detail(pages[href]) if pages.get(href) else {}
        name = info.get("name") or (strs[0] if strs else None)
        if not name:
            continue
        tagline = strs[2] if len(strs) > 2 else None
        stage_raw = info.get("investment_stage") or (strs[1] if len(strs) > 1 else None)
        lp = info.get("location_parts") or []
        # parts are region, country, city (city sometimes truncated on-site)
        city = lp[2] if len(lp) > 2 else None
        country = lp[1] if len(lp) > 1 else None
        location = ", ".join(x for x in (city, country) if x) or (lp[0] if lp else None)
        desc = info.get("desc")
        out.append({
            "company_name": name,
            "description": desc or tagline,
            "tagline": tagline,
            "company_url": clean_url(info.get("site")) if info.get("site") else None,
            "location": location,
            "region": lp[0] if lp else None,
            "country": country,
            "city": city,
            "investment_stage": stage_raw,
            "stage": stage_label(stage_raw),
            "impact_kpis": info.get("impact_kpis") or [],
            "everywhere_tags": tags_for(name, " ".join(x for x in (tagline, desc) if x), [], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "profile_url": href,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "tagline", "company_url", "location", "stage", "investment_stage", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
