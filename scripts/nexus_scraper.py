#!/usr/bin/env python3
"""Nexus Venture Partners portfolio scraper -> nexus_companies.json
Source: https://www.nexusvp.com/companies — Webflow CMS list, paginated
(`?<hash>_page=N`). Each `.companies_item` carries a one-line description and
hidden Finsweet list fields: name, location (U.S. / India), outcome (Active /
M&A / IPO), stage (round Nexus invested at: Pre-Seed / Seed / Series A /
Series B) and category (AI / Consumer / Enterprise / Frontier Tech / Open
Source). Detail pages are client-rendered (no extra data) and are not used.
stage = "Stage Invested" round. outcome M&A -> acquired, Active -> active;
IPO kept as outcome only. No company websites published on the list.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, tags_for, stage_label, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://www.nexusvp.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "nexus_companies.json")
PRIMARY = "Nexus Venture Partners"
SECTOR_TAG_MAP = {"open source": ["Dev Tools / Cloud"], "frontier tech": ["Deeptech / Robotics / AR/VR"]}
# Hand-reviewed tag fixes (judgment pass, no LLM).
TAG_OVERRIDES = {
    "Aemon.ai": [
        "Dev Tools / Cloud"
    ],
    "AskNicely": [
        "Future of Work",
        "Data & Analytics"
    ],
    "AssetPlus": [
        "FinTech / Insurance"
    ],
    "Capgrid": [
        "Logistics / Supply Chain",
        "Transportation / Mobility"
    ],
    "Cognida.ai": [
        "Future of Work"
    ],
    "Costream": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Covvalent": [
        "Logistics / Supply Chain"
    ],
    "doola": [
        "RegTech/Gov/Legal",
        "FinTech / Insurance"
    ],
    "Ember": [
        "Health",
        "FinTech / Insurance"
    ],
    "Giga": [
        "Future of Work"
    ],
    "Helpshift": [
        "Future of Work"
    ],
    "Intello Labs": [
        "Data & Analytics",
        "Logistics / Supply Chain"
    ],
    "JIFFY.ai": [
        "Future of Work"
    ],
    "Joveo": [
        "Future of Work"
    ],
    "Leaping AI": [
        "Future of Work"
    ],
    "Liminal": [
        "Web3 / Crypto",
        "Cybersecurity"
    ],
    "Metaforms": [
        "Data & Analytics"
    ],
    "Mitigata": [
        "Cybersecurity"
    ],
    "MoveInSync": [
        "Transportation / Mobility",
        "Future of Work"
    ],
    "Neuron7.ai": [
        "Future of Work",
        "Data & Analytics"
    ],
    "Pramaana Labs": [
        "Dev Tools / Cloud",
        "Cybersecurity"
    ],
    "RamAIn": [
        "Future of Work"
    ],
    "Runable": [
        "Future of Work"
    ],
    "Suminter": [
        "CPG",
        "Logistics / Supply Chain"
    ],
    "VenWiz": [
        "Logistics / Supply Chain"
    ],
    "Zingle AI": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Arkin Net": [
        "Dev Tools / Cloud"
    ],
    "Biz2Credit": [
        "FinTech / Insurance"
    ],
    "Map My India": [
        "Transportation / Mobility",
        "Data & Analytics"
    ],
    "Infra.Market": [
        "PropTech",
        "Logistics / Supply Chain"
    ],
    "Delhivery": [
        "Logistics / Supply Chain"
    ],
    "Saber": [
        "FinTech / Insurance",
        "Web3 / Crypto"
    ],
    "Turtlemint": [
        "FinTech / Insurance"
    ],
    "Onsurity": [
        "Health",
        "FinTech / Insurance",
        "Future of Work"
    ],
    "Newton School": [
        "Future of Work",
        "Consumer"
    ],
    "WhiteHat Jr": [
        "Consumer",
        "Future of Work"
    ],
    "QFEX": [
        "FinTech / Insurance"
    ],
    "Clover Health": [
        "Health",
        "FinTech / Insurance"
    ],
    "India Shelter": [
        "FinTech / Insurance",
        "PropTech"
    ]
}
LOC = {"U.S.": "United States", "India": "India"}


def field(it, name):
    return [clean(x.get_text(" ")) for x in it.select(f'[fs-list-field="{name}"]') if clean(x.get_text(" "))]


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".companies_item.w-dyn-item"):
            names = field(it, "name")
            if not names or names[0].lower() in seen:
                continue
            name = names[0]
            seen.add(name.lower())
            a = it.select_one("a.companies_link[href]")
            tl = it.select_one(".companies_text .align-center")
            tagline = clean(tl.get_text(" ")) if tl else None
            loc = (field(it, "location") or [None])[0]
            outcome = (field(it, "outcome") or [None])[0]
            stage_raw = (field(it, "stage") or [None])[0]
            cats = [c for c in field(it, "category") if c not in ("M&A", "IPO", "Featured")]
            oc = (outcome or "").lower()
            out.append({
                "company_name": name,
                "description": tagline,
                "location": LOC.get(loc, loc),
                "outcome": outcome,
                "acquirer": (lambda m: clean(m.group(1)) if m else None)(re.search(r"Acquired by ([^.()]+)", tagline or "")),
                "status": "acquired" if oc in ("m&a", "acquired") else ("active" if oc == "active" else None),
                "stage_invested": stage_raw,
                "stage": stage_label(stage_raw),
                "sectors": cats,
                "everywhere_tags": tags_for(name, tagline, cats, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "profile_url": urljoin(SOURCE_URL, a["href"]) if a else None,
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
    for k in ("description", "location", "outcome", "status", "stage", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
