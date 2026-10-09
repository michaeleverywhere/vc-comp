#!/usr/bin/env python3
"""b2venture portfolio scraper -> b2venture_companies.json
Source: https://www.b2venture.vc/portfolio (btov.vc redirects here) — Webflow CMS
table (Finsweet sort/filter) paginated with ?<hash>_page=N. Columns:
Company | Since | Description | Region | Sector(s); each row links to the
company's website.
Since -> first_invested (the year b2venture's holding began, as labelled);
Region -> location (country). The sector filter also carries exit labels:
"Trade Sale" / "Exited" -> status acquired, "IPO" -> exit_route only. No rounds are
published, so stage stays blank.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, tags_for, clean_url, year_of, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.b2venture.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "b2venture_companies.json")
PRIMARY = "b2venture"
# The sector filter also carries exit labels; split them out.
# "Trade Sale" -> status acquired; "IPO" kept as exit_route only (not an acquisition).
EXIT_LABELS = {"trade sale", "ipo", "exited"}
SECTOR_TAG_MAP = {
    "spacetech": ["Deeptech / Robotics / AR/VR"], "fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"],
    "healthtech": ["Health"], "digital health": ["Health"], "medtech": ["Health"], "biotech": ["BioTech"], "life sciences": ["BioTech"],
    "climate": ["Climate / Sustainability"], "climatetech": ["Climate / Sustainability"], "energy": ["Climate / Sustainability"],
    "proptech": ["PropTech"], "mobility": ["Transportation / Mobility"], "logistics": ["Logistics / Supply Chain"],
    "cybersecurity": ["Cybersecurity"], "security": ["Cybersecurity"], "robotics": ["Deeptech / Robotics / AR/VR"],
    "deeptech": ["Deeptech / Robotics / AR/VR"], "hrtech": ["Future of Work"], "future of work": ["Future of Work"],
    "edtech": ["Future of Work"], "legaltech": ["RegTech/Gov/Legal"], "regtech": ["RegTech/Gov/Legal"], "govtech": ["RegTech/Gov/Legal"],
    "e-commerce": ["Consumer"], "consumer": ["Consumer"], "food": ["CPG"], "foodtech": ["CPG"], "gaming": ["Gaming / Media / Entertainment"],
    "media": ["Gaming / Media / Entertainment"], "crypto": ["Web3 / Crypto"], "blockchain": ["Web3 / Crypto"], "web3": ["Web3 / Crypto"],
    "devtools": ["Dev Tools / Cloud"], "infrastructure": ["Dev Tools / Cloud"], "data": ["Data & Analytics"], "analytics": ["Data & Analytics"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "PAVE Space": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Sitegeist": [
        "Deeptech / Robotics / AR/VR",
        "PropTech"
    ],
    "Augmented Industries": [
        "Future of Work",
        "Deeptech / Robotics / AR/VR"
    ],
    "Hive Robotics": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Nautica Technologies": [
        "Deeptech / Robotics / AR/VR",
        "Climate / Sustainability"
    ],
    "Vestigas": [
        "PropTech",
        "Logistics / Supply Chain"
    ],
    "assemblean": [
        "Logistics / Supply Chain",
        "Deeptech / Robotics / AR/VR"
    ],
    "Flyboard": [
        "Future of Work"
    ],
    "Marvel Fusion": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "The Exploration Company": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Atlas Metrics": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Degura": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "Off": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "MMI": [
        "Health",
        "Deeptech / Robotics / AR/VR"
    ],
    "TextCortex": [
        "Future of Work"
    ],
    "Calvin Risk": [
        "RegTech/Gov/Legal",
        "Data & Analytics"
    ],
    "1KOMMA5°": [
        "Climate / Sustainability",
        "PropTech"
    ],
    "Navan": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "equal1": [
        "Deeptech / Robotics / AR/VR"
    ],
    "moojo": [
        "FinTech / Insurance"
    ],
    "Bilthouse": [
        "FinTech / Insurance",
        "PropTech"
    ],
    "Vantis": [
        "Health"
    ],
    "LatticeFlow": [
        "Dev Tools / Cloud"
    ],
    "Threedy": [
        "Deeptech / Robotics / AR/VR",
        "Data & Analytics"
    ],
    "Sternum": [
        "Cybersecurity"
    ],
    "heartbeat medical": [
        "Health"
    ],
    "Headmade Materials": [
        "Deeptech / Robotics / AR/VR"
    ],
    "gitti": [
        "CPG",
        "Consumer"
    ],
    "Decentriq": [
        "Cybersecurity",
        "Data & Analytics"
    ],
    "Neptune": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
    "HQS Quantum Simulations": [
        "Deeptech / Robotics / AR/VR",
        "BioTech"
    ],
    "DessIA": [
        "Deeptech / Robotics / AR/VR",
        "Future of Work"
    ],
    "DEMECAN": [
        "Health"
    ],
    "Incredo": [
        "CPG"
    ],
    "Stamp": [
        "Consumer",
        "FinTech / Insurance"
    ],
    "Chattermill": [
        "Data & Analytics"
    ],
    "Blue Circle": [
        "CPG",
        "Climate / Sustainability"
    ],
    "Hem": [
        "Consumer"
    ],
    "Luciole Medical": [
        "Health"
    ],
    "Flytrex": [
        "Logistics / Supply Chain",
        "Transportation / Mobility",
        "Deeptech / Robotics / AR/VR"
    ],
    "DyeMansion": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Codasip": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Volocopter": [
        "Transportation / Mobility",
        "Deeptech / Robotics / AR/VR"
    ],
    "NVision Imaging": [
        "Health",
        "Deeptech / Robotics / AR/VR"
    ],
    "KIVU": [
        "Cybersecurity"
    ],
    "INZMO": [
        "FinTech / Insurance",
        "PropTech"
    ],
    "foodspring": [
        "CPG",
        "Consumer"
    ],
    "eperi": [
        "Cybersecurity"
    ],
    "BigRep": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Arktis Radiation Detectors Ltd.": [
        "Deeptech / Robotics / AR/VR",
        "RegTech/Gov/Legal"
    ],
    "Websitebutler": [
        "Dev Tools / Cloud"
    ],
    "Testbirds": [
        "Dev Tools / Cloud"
    ],
    "Comtravo": [
        "Transportation / Mobility",
        "Future of Work"
    ],
    "Nestpick": [
        "PropTech",
        "Consumer"
    ],
    "Exosome Diagnostics": [
        "Health",
        "BioTech"
    ],
    "Data Artisans": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
    "Campanda": [
        "Consumer",
        "Transportation / Mobility"
    ],
    "Beekeeper": [
        "Future of Work"
    ],
    "AYOXXA": [
        "BioTech"
    ],
    "Ondeso": [
        "Cybersecurity",
        "Deeptech / Robotics / AR/VR"
    ],
    "Nanda Technologies": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Auxilium": [
        "Health"
    ],
    "Zynga": [
        "Gaming / Media / Entertainment"
    ],
    "DeepL": [
        "Future of Work",
        "Dev Tools / Cloud"
    ],
    "Facebook": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "Xing": [
        "Future of Work",
        "Consumer"
    ],
    "Baze": [
        "Health",
        "CPG"
    ],
    "Mobile GARANTIE": [
        "FinTech / Insurance"
    ],
    "mobile GARANTIE": [
        "FinTech / Insurance"
    ],
    "Synfioo": [
        "Logistics / Supply Chain"
    ],
    "Skoove": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "Sharpist": [
        "Future of Work"
    ],
    "Fruitcore": [
        "Deeptech / Robotics / AR/VR"
    ],
    "CrediMarket": [
        "FinTech / Insurance",
        "Consumer"
    ],
    "Triplemint": [
        "PropTech"
    ],
    "Joblift": [
        "Future of Work"
    ],
    "COMATCH": [
        "Future of Work"
    ],
    "Codecheck": [
        "Consumer"
    ],
    "altoida": [
        "Health"
    ],
    "Vamstar": [
        "Health",
        "Logistics / Supply Chain"
    ],
    "Retinai": [
        "Health",
        "BioTech"
    ],
    "SemanTree Medical": [
        "Health"
    ],
    "Hitmeister": [
        "Consumer"
    ],
    "ecolytiq": [
        "Climate / Sustainability",
        "FinTech / Insurance"
    ],
    "Equippo": [
        "Logistics / Supply Chain",
        "PropTech"
    ],
    "Urban Connect": [
        "Transportation / Mobility",
        "Future of Work"
    ],
    "Forget Finance": [
        "FinTech / Insurance",
        "Consumer"
    ],
    "Electrochaea": [
        "Climate / Sustainability"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select("div.company-item.w-dyn-item"):
            f = lambda k: next((clean(x.get_text(" ")) for x in it.select(f'[fs-cmssort-field="{k}"]') if clean(x.get_text(" "))), None)
            name = f("name")
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            dd = it.select_one(".portfolio-description")
            desc = clean(dd.get_text(" ")) if dd else None
            labels = [clean(x.get_text(" ")) for x in it.select('[fs-cmsfilter-field="sector"]') if clean(x.get_text(" "))]
            exits = [x for x in labels if x.lower() in EXIT_LABELS]
            sectors = [x for x in labels if x.lower() not in EXIT_LABELS]
            link = it.select_one("a[href^=http]")
            since = year_of(f("year"))
            out.append({
                "company_name": name,
                "description": desc,
                "company_url": clean_url(link["href"]) if link else None,
                "first_invested": str(since) if since else None,
                "location": f("region"),
                "status": "acquired" if any(x.lower() in ("trade sale", "exited") for x in exits) else None,
                "exit_route": exits[0] if exits else None,
                "sectors": sectors,
                "everywhere_tags": tags_for(name, desc or "", sectors, SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
            if limit and len(out) >= limit:
                break
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "first_invested", "location", "status", "exit_route", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
