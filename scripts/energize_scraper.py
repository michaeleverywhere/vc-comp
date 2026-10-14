#!/usr/bin/env python3
"""Energize Capital (Energize Ventures) portfolio scraper -> energize_companies.json
Source: https://www.energize.vc/portfolio — Webflow CMS .portfolio-collection-item
cards (fund tags, industry category, "SINCE <year>", one-line description, website,
"why we invested" insight link). Cards carry no name text: the name comes from the
"why-we-invested-in-<slug>" link when present, else the logo file name.
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import unquote
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://www.energize.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "energize_companies.json")
PRIMARY = "Energize Capital"
FUNDS = {"ventures i", "ventures ii", "ventures iii", "venture i", "endurance"}
SECTOR_TAG_MAP = {
    "energy transition": ["Climate / Sustainability"], "decarbonization": ["Climate / Sustainability"],
    "industrial digitization": [], "critical infrastructure": [],
}
NAME_FIX = {"Ncx": "NCX", "Emerald Ai": "Emerald AI", "Zededa Energize Ventures": "Zededa", "Volta Charging": "Volta", "Awake Security": "Awake Security"}
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "Avathon": ["Data & Analytics"], "Greenlite": ["RegTech/Gov/Legal", "PropTech"], "Nixtla": ["Data & Analytics", "Dev Tools / Cloud"],
    "Zededa": ["Dev Tools / Cloud"], "Finite State": ["Cybersecurity"], "Smartcar": ["Transportation / Mobility", "Dev Tools / Cloud"],
    "Monta": ["Climate / Sustainability", "Transportation / Mobility"], "Aurora Solar": ["Climate / Sustainability"],
    "Urbint": ["Data & Analytics", "Climate / Sustainability"], "Handle": ["PropTech", "FinTech / Insurance"],
    "Felt": ["Data & Analytics"], "Instalily": ["Future of Work"],
}


def name_from(card):
    for a in card.select("a.portfolio-link[href]"):
        m = re.search(r"why-(?:we|were)-invest(?:ed|ing)-(?:in-)?([a-z0-9-]+)", a["href"])
        if m:
            n = m.group(1).replace("-", " ").title()
            return NAME_FIX.get(n, n)
    img = card.select_one("img.portfolio-card-image")
    if img:
        fn = re.sub(r"^[0-9a-f]{24}_", "", unquote(img["src"].split("/")[-1]))
        fn = re.sub(r"(?i)[-_ ]*(website )?logo.*$", "", fn.rsplit(".", 1)[0])
        return clean(fn.replace("-", " ").title())
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio-collection-item"):
        name = name_from(it)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cats = [clean(x.get_text()) for x in it.select("[fs-list-field=categories]") if clean(x.get_text())]
        funds = [c for c in cats if c.lower() in FUNDS]
        sectors = [c for c in cats if c.lower() not in FUNDS]
        since = it.select_one(".portfolio-tag-two")
        yr = re.search(r"(19|20)\d\d", since.get_text()) if since else None
        d = it.select_one(".portfolio-middle-card-two .text-size-small")
        site = next((a["href"] for a in it.select("a.portfolio-link[href^=http]") if "energizecap.com" not in a["href"]), None)
        insight = next((a["href"] for a in it.select("a.portfolio-link[href]") if "why-" in a["href"]), None)
        if site:
            m = re.match(r"(https?://[^/]+)/(hubspot_forms|home)\b.*", site)
            site = m.group(1) + "/" if m else site
        out.append({
            "company_name": name,
            "description": clean(d.get_text(" ")) if d else None,
            "company_url": (site if site and re.match(r"https?://(www\.)?ncx\.com", site) else clean_url(site)) if site else None,
            "sectors": sectors,
            "funds": funds,
            "first_invested": int(yr.group(0)) if yr else None,
            "insight_url": ("https://www.energize.vc" + insight) if insight and insight.startswith("/") else insight,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"], r["sectors"], SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "sectors", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
