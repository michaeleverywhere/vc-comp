#!/usr/bin/env python3
"""Bling Capital portfolio scraper -> bling_companies.json
Source: https://www.blingcap.com/portfolio — server-rendered (Next.js) grid of
cards: h3 name, one-line description, optional status line ("Acquired",
"Acquired by X", "Public: TICKER", "Stealth") and the company website as the
card link. Duplicates (featured + full grid) are collapsed by name.
"Acquired" / "Acquired by X" -> status acquired (+ acquirer);
"Public: TICKER" -> public_ticker + exit_route "IPO" (status left blank: not
an acquisition). Stealth cards are kept only when they show a real name.
No rounds, dates or locations are published.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.blingcap.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "bling_companies.json")
PRIMARY = "Bling Capital"
SECTOR_TAG_MAP = {}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Palantir": [
        "Data & Analytics",
        "RegTech/Gov/Legal"
    ],
    "Instacart": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "Rippling": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "Airtable": [
        "Future of Work",
        "Dev Tools / Cloud"
    ],
    "Lime": [
        "Transportation / Mobility"
    ],
    "Lucidchart": [
        "Future of Work"
    ],
    "GitLab": [
        "Dev Tools / Cloud"
    ],
    "Udemy": [
        "Consumer",
        "Future of Work"
    ],
    "Quora": [
        "Consumer",
        "Gaming / Media / Entertainment"
    ],
    "Parse": [
        "Dev Tools / Cloud"
    ],
    "Everlane": [
        "Consumer",
        "CPG"
    ],
    "Hellosign": [
        "Future of Work",
        "RegTech/Gov/Legal"
    ],
    "Quartzy": [
        "BioTech",
        "Logistics / Supply Chain"
    ],
    "Pindrop": [
        "Cybersecurity"
    ],
    "Remind": [
        "Future of Work",
        "Consumer"
    ],
    "DogVacay": [
        "Consumer"
    ],
    "Periscope": [
        "Data & Analytics"
    ],
    "Chewse": [
        "CPG",
        "Future of Work"
    ],
    "ThirdLove": [
        "Consumer",
        "CPG"
    ],
    "Honeybook": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "Zenefits": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "Gobble": [
        "CPG",
        "Consumer"
    ],
    "Quantopian": [
        "FinTech / Insurance"
    ],
    "Plum": [
        "CPG",
        "Consumer"
    ],
    "Canary": [
        "Cybersecurity",
        "Consumer"
    ],
    "Webflow": [
        "Dev Tools / Cloud"
    ],
    "Breeze": [
        "Consumer",
        "Transportation / Mobility"
    ],
    "Gallant": [
        "Health"
    ],
    "Somewear": [
        "Deeptech / Robotics / AR/VR"
    ],
    "GatherAI": [
        "Deeptech / Robotics / AR/VR",
        "Logistics / Supply Chain"
    ],
    "Proxxi": [
        "Deeptech / Robotics / AR/VR",
        "Future of Work"
    ],
    "Actuate": [
        "Cybersecurity"
    ],
    "Printify": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "Alcove": [
        "PropTech"
    ],
    "Tone": [
        "Consumer"
    ],
    "Mobot": [
        "Deeptech / Robotics / AR/VR",
        "Dev Tools / Cloud"
    ],
    "Geologie": [
        "Consumer",
        "CPG"
    ],
    "Merlin Labs": [
        "Transportation / Mobility",
        "Deeptech / Robotics / AR/VR"
    ],
    "Hermeus": [
        "Transportation / Mobility",
        "Deeptech / Robotics / AR/VR"
    ],
    "Birdy Grey": [
        "Consumer",
        "CPG"
    ],
    "Monkeylearn": [
        "Data & Analytics"
    ],
    "NuBrakes": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Honeycomb": [
        "Consumer"
    ],
    "Capitalize": [
        "FinTech / Insurance"
    ],
    "Tinycare": [
        "Consumer"
    ],
    "Grata": [
        "FinTech / Insurance",
        "Data & Analytics"
    ],
    "Kolors": [
        "Transportation / Mobility"
    ],
    "Hellometer": [
        "Data & Analytics",
        "Consumer"
    ],
    "HomePace": [
        "FinTech / Insurance",
        "PropTech"
    ],
    "GoodTrust": [
        "Consumer"
    ],
    "Tempo": [
        "Consumer",
        "Health"
    ],
    "Prive": [
        "Consumer"
    ],
    "Ignition": [
        "Future of Work"
    ],
    "Treet": [
        "Consumer"
    ],
    "Beaubble": [
        "Consumer",
        "CPG"
    ],
    "Vista": [
        "Cybersecurity",
        "Dev Tools / Cloud"
    ],
    "Lyte": [
        "Climate / Sustainability",
        "Transportation / Mobility"
    ],
    "Dutch": [
        "Health"
    ],
    "Fountain": [
        "Future of Work"
    ],
    "Enclave": [
        "PropTech"
    ],
    "Hansa": [
        "Consumer"
    ],
    "Taelor": [
        "Consumer"
    ],
    "VetVet": [
        "Health"
    ],
    "Wally": [
        "Health"
    ],
    "Optiversal": [
        "Consumer"
    ],
    "DataroomHQ": [
        "FinTech / Insurance",
        "Data & Analytics"
    ],
    "Atrix": [
        "BioTech",
        "RegTech/Gov/Legal"
    ],
    "Unthread": [
        "Future of Work"
    ],
    "Alma": [
        "RegTech/Gov/Legal"
    ],
    "Maneva": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Recess": [
        "Consumer"
    ],
    "Careem": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Hims & Hers": [
        "Health",
        "Consumer"
    ],
    "Matterport": [
        "PropTech",
        "Deeptech / Robotics / AR/VR"
    ],
    "Odyssey": [
        "FinTech / Insurance",
        "Consumer"
    ],
    "Cavalry": [
        "Consumer"
    ],
    "Bites": [
        "Consumer"
    ],
    "Companion Home": [
        "Consumer"
    ],
    "Snow Diamonds": [
        "Consumer",
        "CPG"
    ],
    "Elaborate": [
        "Health"
    ],
    "Jiffy": [
        "PropTech",
        "Consumer"
    ],
    "Ostro": [
        "Health"
    ],
    "Titan": [
        "Future of Work"
    ],
    "Jack Archer": [
        "Consumer",
        "CPG"
    ],
    "Agent": [
        "FinTech / Insurance"
    ],
    "Assemble": [
        "Health",
        "Future of Work"
    ],
    "Boop": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Brightlights": [
        "Gaming / Media / Entertainment"
    ],
    "Carbon AI": [
        "FinTech / Insurance",
        "PropTech"
    ],
    "Care Comply": [
        "RegTech/Gov/Legal",
        "Health"
    ],
    "Dazzle": [
        "Consumer"
    ],
    "DoubleO": [
        "Future of Work"
    ],
    "Featurely": [
        "Data & Analytics"
    ],
    "Gobi Maps": [
        "Consumer"
    ],
    "Halo Beauty": [
        "CPG",
        "Deeptech / Robotics / AR/VR"
    ],
    "Hero Safety": [
        "Cybersecurity",
        "Future of Work"
    ],
    "Jano": [
        "Health"
    ],
    "Loti": [
        "Cybersecurity",
        "Consumer"
    ],
    "Loyalist": [
        "Consumer"
    ],
    "Mont Wealth": [
        "FinTech / Insurance"
    ],
    "Narada": [
        "Future of Work"
    ],
    "OpsHelm": [
        "Dev Tools / Cloud",
        "Cybersecurity"
    ],
    "Parambil": [
        "RegTech/Gov/Legal",
        "Health"
    ],
    "Paratus": [
        "RegTech/Gov/Legal"
    ],
    "Peerbound": [
        "Future of Work"
    ],
    "Reflow": [
        "Dev Tools / Cloud"
    ],
    "Rosie": [
        "Consumer"
    ],
    "Shade": [
        "Gaming / Media / Entertainment",
        "Dev Tools / Cloud"
    ],
    "Showdrop": [
        "Consumer",
        "CPG"
    ],
    "Sidecar Data": [
        "Data & Analytics"
    ],
    "Snag": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "Span": [
        "Dev Tools / Cloud"
    ],
    "Tuyo": [
        "Health"
    ],
    "Ultra": [
        "CPG"
    ],
    "Versable": [
        "Data & Analytics",
        "Logistics / Supply Chain"
    ],
    "Pear": [
        "Consumer"
    ],
    "Argentic": [
        "FinTech / Insurance"
    ],
    "Autena": [
        "Logistics / Supply Chain"
    ],
    "Atomiq Labs": [
        "Future of Work"
    ],
    "Oureon": [
        "Deeptech / Robotics / AR/VR",
        "RegTech/Gov/Legal"
    ],
    "Ember AI": [
        "Dev Tools / Cloud"
    ],
    "Decisive AI": [
        "Dev Tools / Cloud"
    ],
    "Musically": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Figure": [
        "FinTech / Insurance"
    ],
    "Blaze": [
        "Data & Analytics"
    ],
    "Sunbound": [
        "FinTech / Insurance",
        "Health"
    ],
    "Gusto": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "Spellbook": [
        "RegTech/Gov/Legal"
    ],
    "Kodif": [
        "Future of Work",
        "Consumer"
    ],
    "Carbon": [
        "FinTech / Insurance"
    ],
    "Mangrove Systems": [
        "Climate / Sustainability"
    ],
    "Flotive": [
        "Climate / Sustainability",
        "RegTech/Gov/Legal"
    ],
    "Lever": [
        "Future of Work"
    ],
    "Wattpad": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Snapp Stats": [
        "Data & Analytics",
        "Gaming / Media / Entertainment"
    ],
    "Pod": [
        "Future of Work"
    ],
    "Klutch": [
        "PropTech",
        "Future of Work"
    ],
    "Commenda": [
        "RegTech/Gov/Legal",
        "FinTech / Insurance"
    ],
    "Onclaim": [
        "FinTech / Insurance",
        "RegTech/Gov/Legal"
    ],
    "Dobby": [
        "Logistics / Supply Chain"
    ],
    "Hamilton AI": [
        "Transportation / Mobility"
    ],
    "EyesATop": [
        "Deeptech / Robotics / AR/VR",
        "RegTech/Gov/Legal"
    ],
    "Formula Health": [
        "Health",
        "CPG"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for a in soup.find_all("a"):
        cls = a.get("class") or []
        if "group" not in cls or "bg-white" not in cls or not a.find("h3"):
            continue
        name = clean(a.find("h3").get_text(" "))
        if not name or name.lower() in seen or name.lower() == "stealth":
            continue
        seen.add(name.lower())
        ps = a.find_all("p")
        desc = clean(ps[0].get_text(" ")) if ps else None
        if desc and desc.lower() == "stealth":
            desc = None
        st = next((clean(p.get_text(" ")) for p in ps if "text-xs" in (p.get("class") or [])), None)
        status = acquirer = ticker = route = None
        if st:
            m = re.match(r"(?i)acquired(?:\s+by\s+(.+))?$", st)
            if m:
                status, acquirer = "acquired", clean(m.group(1))
            m = re.match(r"(?i)public:\s*(\S+)", st)
            if m:
                ticker, route = m.group(1).upper(), "IPO"
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a.get("href", "").startswith("http") else None,
            "status": status,
            "site_status": st,
            "acquirer": acquirer,
            "public_ticker": ticker,
            "exit_route": route,
            "everywhere_tags": tags_for(name, desc or "", [], SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "acquirer", "public_ticker", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
