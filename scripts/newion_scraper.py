#!/usr/bin/env python3
"""Newion portfolio scraper -> newion_companies.json
Source: https://www.newion.com/portfolio — Webflow CMS (server-rendered, single
page). Two collection lists share the company name as an attribute:
`div.portfolio-item[portfolio=<name>]` rows (city, country, investment year,
status active/exited) and `div.portfolio-item-popup[portfolio-item=<name>]`
popups (About text, "Date of Investment", Newion team, website button).
Date of Investment -> first_invested; "City, Country" -> location;
active -> active, exited -> acquired (raw label kept in site_status).
No rounds are published.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, year_of, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.newion.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "newion_companies.json")
PRIMARY = "Newion"
STATUS = {"active": "active", "exited": "acquired"}
SECTOR_TAG_MAP = {}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Nopan": [
        "FinTech / Insurance"
    ],
    "Lightbringer": [
        "RegTech/Gov/Legal"
    ],
    "TurnUp": [
        "Health",
        "Data & Analytics"
    ],
    "NjiaPay": [
        "FinTech / Insurance"
    ],
    "Agileday": [
        "Future of Work"
    ],
    "Birdsview": [
        "Future of Work",
        "Consumer"
    ],
    "SEQUESTO": [
        "Future of Work",
        "Data & Analytics"
    ],
    "nuwacom": [
        "Future of Work",
        "Gaming / Media / Entertainment"
    ],
    "Ellie.ai": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Occtoo": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "LegionellaDossier": [
        "PropTech",
        "RegTech/Gov/Legal"
    ],
    "Prepr": [
        "Dev Tools / Cloud",
        "Gaming / Media / Entertainment"
    ],
    "Passendo": [
        "Gaming / Media / Entertainment"
    ],
    "Salonkee": [
        "Future of Work",
        "Consumer"
    ],
    "Dexter": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Filestage": [
        "Future of Work"
    ],
    "APICBASE NV": [
        "Logistics / Supply Chain",
        "CPG"
    ],
    "REXai": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
    "Roadmap": [
        "Future of Work"
    ],
    "PlayPass": [
        "Gaming / Media / Entertainment",
        "Cybersecurity"
    ],
    "Oxynade": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Synple": [
        "Logistics / Supply Chain"
    ],
    "L1nda": [
        "Future of Work"
    ],
    "The Next Ad": [
        "Gaming / Media / Entertainment"
    ],
    "Nallian": [
        "Logistics / Supply Chain",
        "Data & Analytics"
    ],
    "Foleon": [
        "Gaming / Media / Entertainment",
        "Future of Work"
    ],
    "24/i": [
        "Gaming / Media / Entertainment"
    ],
    "iWelcome": [
        "Cybersecurity"
    ],
    "Collibra": [
        "Data & Analytics"
    ],
    "Mirror42": [
        "Data & Analytics"
    ],
    "XVR Simulation": [
        "Deeptech / Robotics / AR/VR",
        "RegTech/Gov/Legal"
    ],
    "Q-GO": [
        "Data & Analytics"
    ],
    "Asysco": [
        "Dev Tools / Cloud"
    ],
    "Wisdom TMLC": [
        "Dev Tools / Cloud"
    ],
    "Minihouse": [
        "Logistics / Supply Chain",
        "RegTech/Gov/Legal"
    ],
    "Servoy": [
        "Dev Tools / Cloud"
    ],
    "Reasult": [
        "FinTech / Insurance",
        "PropTech"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    popups = {clean(p.get("portfolio-item")).lower(): p for p in soup.select("div.portfolio-item-popup[portfolio-item]") if clean(p.get("portfolio-item"))}
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for row in soup.select("div.portfolio-item[portfolio]"):
        t = row.select_one("p.title")
        name = clean(t.get_text(" ")) if t else clean(row.get("portfolio"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        city = clean(row.select_one(".city-wrapper p").get_text(" ")) if row.select_one(".city-wrapper p") else None
        country = clean(row.select_one("p.country").get_text(" ")) if row.select_one("p.country") else None
        ps = [clean(p.get_text(" ")) for p in row.select(".portfolio-item-wrapper > p") if clean(p.get_text(" "))]
        year = next((year_of(x) for x in ps if re.fullmatch(r"(19|20)\d\d", x)), None)
        raw_status = next((x for x in ps if x.lower() in STATUS), None)
        pop = popups.get(clean(row.get("portfolio") or name).lower())
        desc = site = None
        team = []
        if pop:
            rt = pop.select_one(".w-richtext")
            desc = clean(rt.get_text(" ")) if rt else None
            a = pop.select_one("a.url-to-be-added-to-btn[href^=http]")
            site = a["href"] if a else None
            team = [clean(p.get_text(" ")) for p in pop.select(".collection-item-3 p") if clean(p.get_text(" "))]
            if not year:
                for w in pop.select(".p-title-wrapper"):
                    lab = w.find("p")
                    if lab and "date of investment" in lab.get_text(" ").lower():
                        year = year_of(w.get_text(" "))
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(site) if site else None,
            "status": STATUS.get((raw_status or "").lower()),
            "site_status": raw_status,
            "first_invested": str(year) if year else None,
            "location": ", ".join(x for x in (city, country) if x) or None,
            "investor_team": team,
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
    for k in ("description", "company_url", "status", "first_invested", "location", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
