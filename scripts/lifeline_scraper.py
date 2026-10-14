#!/usr/bin/env python3
"""Lifeline Ventures portfolio scraper -> lifeline_companies.json
Source: https://lifelineventures.com/companies/ — SSR .companies__item blocks
(data-sector, data-status, description, CEO/founders, website, and a funding
timeline: Founded year, Lifeline's entry round + year, later rounds with leads).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, stage_label, prune_substring_tags, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://lifelineventures.com/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "lifeline_companies.json")
PRIMARY = "Lifeline Ventures"
SECTOR_TAG_MAP = {
    "health": ["Health"], "healthcare": ["Health"], "health-tech": ["Health"], "life-science": ["BioTech", "Health"],
    "games": ["Gaming / Media / Entertainment"], "gaming": ["Gaming / Media / Entertainment"],
    "hardware": ["Deeptech / Robotics / AR/VR"], "deeptech": ["Deeptech / Robotics / AR/VR"],
    "software": [], "consumer": ["Consumer"], "climatetech": ["Climate / Sustainability"],
    "energy": ["Climate / Sustainability"], "financial": ["FinTech / Insurance"], "techbio": ["BioTech"],
    "defence": ["Deeptech / Robotics / AR/VR"], "social-media": ["Consumer"], "marketplace": [], "b2b-saas": [], "tech": [],
}
EXIT_RX = re.compile(r"(?i)exit|acquir|ipo|merg|majority|listing|sold")
STATUS_MAP = {"current": "active", "exited": "acquired", "exit": "acquired", "ipo": "live"}
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "Vensum Power": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "HyCom Core": ["Deeptech / Robotics / AR/VR"],
    "Realstocks": ["FinTech / Insurance", "PropTech"],
    "Moves": ["Health", "Consumer"],
    "Candela 683": ["Gaming / Media / Entertainment", "Consumer"], "Curious AI": ["Dev Tools / Cloud"],
    "Elea & Lili": ["BioTech", "Deeptech / Robotics / AR/VR"], "IndoorAtlas": ["Dev Tools / Cloud", "Data & Analytics"],
    "Mobal": ["Future of Work"], "Nordcraft": ["Dev Tools / Cloud"], "Smartly.io": ["Gaming / Media / Entertainment", "Data & Analytics"],
    "Tinkercad": ["Dev Tools / Cloud", "Deeptech / Robotics / AR/VR"], "Ambio": ["Logistics / Supply Chain"],
    "BetterDoctor": ["Health", "Data & Analytics"], "Clouder": ["PropTech", "Climate / Sustainability"],
    "CurifyLabs": ["Health", "BioTech"], "Deep Measures": ["Health", "BioTech", "Data & Analytics"],
    "Hyperion Robotics": ["Deeptech / Robotics / AR/VR", "PropTech", "Climate / Sustainability"],
    "Karsa": ["Health", "Deeptech / Robotics / AR/VR"], "Kayzen": ["Gaming / Media / Entertainment", "Data & Analytics"],
    "Mindfield Games": ["Gaming / Media / Entertainment", "Deeptech / Robotics / AR/VR"],
    "NextInox / Solu Stainless": ["Deeptech / Robotics / AR/VR", "Climate / Sustainability"],
    "Ninchat": ["Future of Work", "Dev Tools / Cloud"], "Origin by Ocean": ["Climate / Sustainability", "BioTech"],
    "Photoncycle": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"], "Realm": ["Future of Work", "Data & Analytics"],
    "Risk Ledger": ["Cybersecurity", "Logistics / Supply Chain"], "School Day": ["Health", "Data & Analytics"],
    "Sensofusion": ["Cybersecurity", "Deeptech / Robotics / AR/VR"], "Soldera": ["Climate / Sustainability", "FinTech / Insurance"],
    "Solu": ["BioTech", "Health"], "Spacent": ["PropTech"], "Thinglink": ["Gaming / Media / Entertainment"],
    "Token Terminal": ["Web3 / Crypto", "Data & Analytics"], "Vaire": ["Deeptech / Robotics / AR/VR"],
    "Verda": ["Dev Tools / Cloud"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".companies__item"):
        h2 = it.select_one(".company-info h2")
        name = clean(h2.get_text(" ")) if h2 else clean(it.get("data-company"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc, ceo, founders = None, None, []
        for p in it.select(".company-info > p"):
            t = p.get_text("\n")
            if re.search(r"(?m)^\s*(CEO|Founders?)\s*:", t):
                for line in t.split("\n"):
                    line = clean(line)
                    if not line:
                        continue
                    if line.lower().startswith("ceo:"):
                        ceo = clean(line.split(":", 1)[1])
                    elif re.match(r"(?i)founders?:", line):
                        founders = [clean(x) for x in line.split(":", 1)[1].split(",") if clean(x)]
            elif not desc and clean(t):
                desc = clean(t)
        a = it.select_one(".links a.external-link[href^=http]")
        founded, entry_year, entry_round, rounds = None, None, None, []
        for ti in it.select(".timeline__item"):
            yr = clean(ti.select_one(".year").get_text()) if ti.select_one(".year") else None
            title = clean(ti.select_one(".title").get_text()) if ti.select_one(".title") else None
            pre = clean(ti.select_one(".pretitle").get_text()) if ti.select_one(".pretitle") else None
            sub = clean(ti.select_one(".subtitle").get_text()) if ti.select_one(".subtitle") else None
            if title and title.lower() == "founded":
                founded = int(yr) if yr and yr.isdigit() else None
                continue
            rnd = {"year": int(yr) if yr and yr.isdigit() else None, "round": title, "note": sub}
            rounds.append(rnd)
            if pre and "lifeline" in pre.lower() and entry_year is None:
                entry_year, entry_round = rnd["year"], title
        last = next((r for r in reversed(rounds) if r.get("round") and not EXIT_RX.search(r["round"])), None)
        sector = clean(it.get("data-sector"))
        status_raw = clean(it.get("data-status"))
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a else None,
            "sectors": [sector] if sector else [],
            "ceo": ceo,
            "founders": founders,
            "year_founded": founded,
            "stage": stage_label(entry_round) if entry_round else None,
            "entry_round_raw": entry_round,
            "first_invested": entry_year,
            "last_financing": (f"{last['round']} ({last['year']})" + (f" — {last['note']}" if last.get("note") else "")) if last else None,
            "funding_timeline": rounds,
            "site_status": status_raw,
            "status": STATUS_MAP.get((status_raw or "").lower()),
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        rec["everywhere_tags"] = tags_for(name, desc, rec["sectors"], SECTOR_TAG_MAP)
        out.append(rec)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "stage", "first_invested", "last_financing", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
