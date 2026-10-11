#!/usr/bin/env python3
"""AlleyCorp portfolio scraper -> alleycorp_companies.json
Source: https://alleycorp.com/companies/ — WordPress (Salient post grid); each
.nectar-post-grid-item has the name, a meta line "<Incubation|Investment> |
<status>" (status e.g. Acquired / NASDAQ: MDB / NYSE: ...) and a one-line
description. Incubation cards link to a detail page (/companies/<slug>/) that adds founders, a Highlights line
and the "Visit Website" link; Investment cards link straight to the company's
own website (used as company_url). status: "Acquired" -> acquired; public listings
kept verbatim in site_status. No location, round or year published.
"""
import os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, fetch_many, clean, tags_for, clean_url, label_after,
                             prune_substring_tags, apply_tag_overrides, is_social)
from _d20_common import write_out

SOURCE_URL = "https://alleycorp.com/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "alleycorp_companies.json")
PRIMARY = "AlleyCorp"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed judgment tags (no LLM), 2026-10-11
    "Business Insider": ["Gaming / Media / Entertainment"],
    "Gilt Groupe": ["Consumer"],
    "Pearl Health": ["Health"],
    "Valar Atomics": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Radical AI": ["Deeptech / Robotics / AR/VR"],
    "Pathway Labs": ["Health"],
    "Epsilon Health": ["Health"],
    "Zola": ["Consumer"],
    "Eyebot": ["Health"],
    "Upwage": ["Future of Work", "FinTech / Insurance"],
    "World Class Health": ["Health"],
    "Henry Capital": ["FinTech / Insurance"],
    "Lazo": ["FinTech / Insurance"],
    "Halo Braid": ["Deeptech / Robotics / AR/VR", "Consumer"],
    "Sanctum": ["Health"],
    "Birches Health": ["Health"],
    "Meetup": ["Consumer"],
    "Coral Care": ["Health"],
    "Addi": ["FinTech / Insurance"],
    "Ansible Health": ["Health"],
    "Siftwell": ["Health"],
    "Vori Health": ["Health"],
    "Spaero Bio": ["BioTech", "Deeptech / Robotics / AR/VR"],
    "For Wellness": ["CPG"],
    "Chamber Cardio": ["Health"],
    "BlackSky": ["Deeptech / Robotics / AR/VR", "Data & Analytics"],
    "Ruby Health": ["Health"],
    "Multiscale Technologies": ["Deeptech / Robotics / AR/VR"],
    "SoBanHang": ["Consumer"],
    "Moons": ["Health", "Consumer"],
    "Nara Organics": ["CPG"],
    "Cascade Health": ["Health"],
    "Positive Development": ["Health"],
    "Atlas Obscura": ["Gaming / Media / Entertainment"],
    "Native Voice": ["Gaming / Media / Entertainment"],
    "Tertulia": ["Consumer", "Gaming / Media / Entertainment"],
    "Dance": ["Transportation / Mobility"],
    "Reddit": ["Consumer", "Gaming / Media / Entertainment"],
    "Knock": ["PropTech"],
    "Printify": ["Consumer"],
    "Aon 3D": ["Deeptech / Robotics / AR/VR"],
    "Buffy": ["CPG"],
    "Mosaic Foods": ["CPG"],
    "Chord Commerce": ["Dev Tools / Cloud", "Consumer"],
    "Pace": ["Dev Tools / Cloud"],
    "Delta One": ["Web3 / Crypto"],
    "Actual AI": ["Future of Work"],
    "Maven": ["Health"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    rows, seen = [], set()
    for it in soup.select(".nectar-post-grid-item"):
        h = it.select_one(".post-heading a[href]")
        if not h:
            continue
        name = clean(h.get_text(" "))
        href = h["href"]
        if not name or href in seen:
            continue
        seen.add(href)
        ex = it.select_one(".meta-excerpt")
        desc, typ, st = None, None, None
        if ex:
            hov = ex.select_one(".comp-hov")
            desc = clean(hov.get_text(" ")) if hov else None
            if hov:
                hov.extract()
            parts = [clean(p) for p in ex.get_text(" ").split("|") if clean(p)]
            typ = parts[0] if parts else None
            st = parts[1] if len(parts) > 1 else None
        rows.append({"name": name, "href": href, "desc": desc, "type": typ, "status": st})
    pages = fetch_many([r["href"] for r in rows if "alleycorp.com" in r["href"]], workers=4)
    out = []
    for r in rows:
        site, founders, highlights = None, [], None
        own = "alleycorp.com" in r["href"]
        if not own:  # Investment cards link straight to the company's own site
            site = clean_url(r["href"])
        html = pages.get(r["href"]) if own else None
        if html:
            d = BeautifulSoup(html, "html.parser")
            for a in d.select("a[href^=http]"):
                if "visit website" in (a.get_text(" ") or "").lower() and not is_social(a["href"]):
                    site = clean_url(a["href"])
                    break
            main_el = d.select_one("main") or d
            strings = list(main_el.stripped_strings)
            highlights = label_after(strings, "Highlights")
            if "Founders" in strings:
                i = strings.index("Founders")
                for s in strings[i + 1:i + 8]:
                    if s in ("Highlights", "About", "Visit Website"):
                        break
                    founders.append(clean(s))
        st = r["status"]
        out.append({
            "company_name": r["name"],
            "description": r["desc"],
            "company_url": site,
            "alleycorp_role": r["type"],
            "site_status": st,
            "status": "acquired" if (st or "").lower().startswith("acquired") else None,
            "highlights": highlights,
            "founders": [f for f in founders if f],
            "everywhere_tags": tags_for(r["name"], r["desc"]),
            "primary_investor": PRIMARY,
            "profile_url": r["href"] if own else None,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "alleycorp_role", "status", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
