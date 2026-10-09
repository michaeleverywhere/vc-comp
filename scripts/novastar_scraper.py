#!/usr/bin/env python3
"""Novastar Ventures portfolio scraper -> novastar_companies.json
Source: https://www.novastarventures.com/portfolio/ — server-rendered WordPress
grid (24 cards: name + tagline) linking to /portfolio/<slug>/ case studies.
Each case study has the narrative description, a founder quote card
("Name / Co-founder"), a "Visit <Company>" website link and a dated timeline
("2022 — Novastar leads BasiGo's seed funding round ...").
first_invested = the earliest timeline year whose entry mentions Novastar;
stage = the round named in that entry, only when one is published.
Acquisitions are taken only from timeline entries saying "acquired by".
No location field is published per company (Novastar invests in Africa).
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, round_label, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.novastarventures.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "novastar_companies.json")
PRIMARY = "Novastar Ventures"
SECTOR_TAG_MAP = {}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "BasiGo": [
        "Transportation / Mobility",
        "Climate / Sustainability",
        "FinTech / Insurance"
    ],
    "Breadfast": [
        "Consumer",
        "CPG",
        "Logistics / Supply Chain"
    ],
    "Chowdeck": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "Elephant": [
        "Health"
    ],
    "GreenPath": [
        "CPG",
        "Climate / Sustainability"
    ],
    "Ignitia": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "iProcure": [
        "Logistics / Supply Chain",
        "CPG"
    ],
    "KOKO Networks": [
        "Climate / Sustainability",
        "Consumer"
    ],
    "Komaza": [
        "Climate / Sustainability"
    ],
    "MAX": [
        "Transportation / Mobility",
        "FinTech / Insurance"
    ],
    "MoKo": [
        "Consumer"
    ],
    "Moniepoint": [
        "FinTech / Insurance"
    ],
    "mPharma": [
        "Health",
        "Logistics / Supply Chain"
    ],
    "NewGlobe": [
        "Future of Work",
        "RegTech/Gov/Legal"
    ],
    "PayGo": [
        "Climate / Sustainability"
    ],
    "Penda": [
        "Health"
    ],
    "poa! Internet": [
        "Consumer",
        "Dev Tools / Cloud"
    ],
    "Regen Organics": [
        "Climate / Sustainability",
        "CPG"
    ],
    "Sistema.bio": [
        "Climate / Sustainability",
        "FinTech / Insurance"
    ],
    "SOKO": [
        "Consumer",
        "CPG"
    ],
    "SolarNow": [
        "Climate / Sustainability",
        "FinTech / Insurance"
    ],
    "Sure Chill": [
        "Climate / Sustainability",
        "Deeptech / Robotics / AR/VR"
    ],
    "TradeDepot": [
        "Logistics / Supply Chain",
        "CPG",
        "FinTech / Insurance"
    ],
    "Turaco": [
        "FinTech / Insurance",
        "Health"
    ],
}


def parse_detail(html, name):
    s = BeautifulSoup(html, "html.parser")
    paras = [clean(p.get_text(" ")) for p in s.select("main .base-text p") if clean(p.get_text(" "))]
    paras = [p for p in paras if not p.startswith("“") and not p.startswith('"')]
    key = name.lower().split()[0]
    desc = next((p for p in paras if p.lower().startswith(key)), None) \
        or next((p for p in paras if key in p.lower()), paras[0] if paras else None)
    site = next((a["href"] for a in s.select("main a[href^=http]") if clean(a.get_text(" ")) and clean(a.get_text(" ")).lower().startswith("visit")), None)
    founders = []
    for p in s.select("main p.opacity-50"):
        lines = [clean(x) for x in p.get_text("\n").split("\n") if clean(x)]
        if len(lines) >= 2 and re.search(r"(?i)founder|\bceo\b", lines[1]) and "novastar" not in lines[1].lower():
            founders.append(lines[0])
    events = []
    for h in s.select("main h3"):
        t = clean(h.get_text(" "))
        if t and re.fullmatch(r"(19|20)\d\d", t):
            p = h.find_next_sibling("p")
            if p and clean(p.get_text(" ")):
                events.append((int(t), clean(p.get_text(" "))))
    events.sort()
    first = next(((y, e) for y, e in events if re.search(r"(?i)novastar|\bNVAF", e)), None)
    acq = next(((y, e) for y, e in events if re.search(r"(?i)\bacquired by\b|\bacquires\b|\bacquisition\b", e)), None)
    acquirer = None
    if acq:
        m = re.search(r"(?i)acquired by ([A-Z][\w&.\- ]+?)(?:[,.;]|$| in | for )", acq[1])
        acquirer = clean(m.group(1)) if m else None
    return {
        "description": desc,
        "company_url": clean_url(site) if site else None,
        "founders": list(dict.fromkeys(founders)),
        "first_invested": first[0] if first else None,
        "stage": (round_label(first[1]) or "").split(" / ")[0] or None if first else None,
        "timeline": [{"year": y, "event": e} for y, e in events],
        "status": "acquired" if acq else None,
        "acquirer": acquirer,
        "exit_year": acq[0] if acq else None,
    }


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    for a in soup.find_all("a", href=True):
        href = urljoin(SOURCE_URL, a["href"])
        if re.search(r"/portfolio/[^/]+/?$", href) and a.find("h4"):
            name = clean(a.find("h4").get_text(" "))
            tag = clean(a.find("h3").get_text(" ")) if a.find("h3") else None
            if name and href not in [c[2] for c in cards]:
                cards.append((name, tag, href))
    if limit:
        cards = cards[:limit]
    pages = fetch_many([c[2] for c in cards])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for name, tag, href in cards:
        d = parse_detail(pages[href], name) if pages.get(href) else {}
        desc = d.get("description") or tag
        out.append({
            "company_name": name,
            "description": desc,
            "tagline": tag,
            "company_url": d.get("company_url"),
            "company_profile_url": href,
            "status": d.get("status"),
            "acquirer": d.get("acquirer"),
            "exit_year": d.get("exit_year"),
            "stage": d.get("stage"),
            "first_invested": d.get("first_invested"),
            "founders": d.get("founders") or [],
            "timeline": d.get("timeline") or [],
            "sectors": [],
            "everywhere_tags": tags_for(name, " ".join(x for x in (tag, desc) if x), [], SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "stage", "first_invested", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
