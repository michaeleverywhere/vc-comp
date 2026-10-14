#!/usr/bin/env python3
"""Moxxie Ventures portfolio scraper -> moxxie_companies.json
Source: https://www.moxxie.vc/ — Webflow CMS logo collection (name from logo alt /
mobile name, one-line description, hidden category field, conditional "Acquired"
badge, website) plus the featured top-portfolio slider ("Name: description").
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.moxxie.vc/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "moxxie_companies.json")
PRIMARY = "Moxxie Ventures"
SECTOR_TAG_MAP = {
    "healthcare": ["Health"],
    "climate": ["Climate / Sustainability"],
    "fintech": ["FinTech / Insurance"],
    "consumer": ["Consumer"],
    "infra": [],
    "enterprise": [],
}
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "Ario": ["Data & Analytics"], "Carta": ["FinTech / Insurance"],
    "Certn": ["Future of Work", "RegTech/Gov/Legal"], "Clubhouse": ["Consumer", "Gaming / Media / Entertainment"],
    "Delve": ["RegTech/Gov/Legal"], "Dreambound": ["Future of Work"],
    "Goodtrust": ["Consumer", "RegTech/Gov/Legal"], "Haptych": ["Health", "Deeptech / Robotics / AR/VR"],
    "Kapiche": ["Data & Analytics"], "Minitap AI": ["Dev Tools / Cloud"], "Orange Slice AI": ["Future of Work"],
    "Parallel": ["Dev Tools / Cloud"], "PlusPlus": ["Future of Work"], "Spellbook": ["RegTech/Gov/Legal"],
    "Spring Cycle Energy": ["Climate / Sustainability"], "Rocket Doctor": ["Health"],
    "Flucta": ["Dev Tools / Cloud", "Deeptech / Robotics / AR/VR"], "Quill AI": ["Health", "FinTech / Insurance"],
    "Bluenote Health": ["Health", "BioTech"], "Phoebe": ["Health"], "Daily.co": ["Dev Tools / Cloud"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], {}
    for it in soup.select(".logo-collection_items > .logo-collection_item"):
        nm = it.select_one(".logo-coloection_name") or it.select_one("img[alt]")
        name = clean(nm.get_text(" ") if nm.name != "img" else nm.get("alt"))
        if not name or name.lower() in seen:
            continue
        a = it.select_one("a[href^=http]")
        dtxt = it.select_one(".slide-logo_text")
        desc = clean(dtxt.get_text(" ")) if dtxt else None
        cats = [clean(c.get_text()) for c in it.select("[fs-list-field=category]") if clean(c.get_text())]
        acq = it.select_one(".logo-coloection_aquired")
        acquired = bool(acq and "w-condition-invisible" not in (acq.get("class") or []))
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a else None,
            "sectors": cats,
            "status": "acquired" if acquired else None,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        seen[name.lower()] = rec
        out.append(rec)
    # featured slider: anchor text "Name: description"
    for a in soup.select(".top-logo-portfolio a[href^=http]"):
        t = clean(a.get_text(" "))
        img = a.find_previous("img")
        name = None
        if t and ":" in t.split(" ")[0] + t[:40]:
            name = clean(t.split(":", 1)[0])
        if not name:
            continue
        rec = seen.get(name.lower())
        if rec:
            rec["description"] = rec["description"] or t
            continue
        rec = {
            "company_name": name, "description": t, "company_url": clean_url(a["href"]),
            "sectors": [], "status": None, "everywhere_tags": [], "primary_investor": PRIMARY,
            "source_url": SOURCE_URL, "scraped_at": scraped_at,
        }
        seen[name.lower()] = rec
        out.append(rec)
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"], r["sectors"], SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
