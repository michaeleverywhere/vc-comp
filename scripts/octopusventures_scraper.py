#!/usr/bin/env python3
"""Octopus Ventures portfolio scraper -> octopusventures_companies.json
Source: https://octopusventures.com/portfolio/ — WordPress (WP Engine) archive,
16 cards per page at /portfolio/page/N/. Each card carries the company name,
a one-line excerpt (description), the company website (card link) and the
sector term as a CSS class. Status comes from the `portfolio-status` taxonomy
archives (/portfolio-status/exited/, /portfolio-status/current/).
Note: some /portfolio/page/N/ URLs are cached as 301s back to page 1 at the
CDN, so every request carries a harmless cache-busting query string.
Status: Current -> active; Exited -> acquired (raw kept in site_status).
No round, investment year or location is published on the cards.
"""
import json, os, sys
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import HEADERS, fetch, fetch_response, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://octopusventures.com/portfolio/"
BASE = "https://octopusventures.com"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "octopusventures_companies.json")
PRIMARY = "Octopus Ventures"
SECTORS = {"b2b-software": "B2B Software", "bio": "Bio", "climate": "Climate", "consumer": "Consumer",
           "deep-tech": "Deep Tech", "fintech": "Fintech", "health": "Health", "pre-seed": "Pre-seed"}
SECTOR_TAG_MAP = {
    "bio": ["BioTech"], "climate": ["Climate / Sustainability"], "consumer": ["Consumer"],
    "deep tech": ["Deeptech / Robotics / AR/VR"], "fintech": ["FinTech / Insurance"], "health": ["Health"],
}
STATUS = {"current": "active", "exited": "acquired"}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Altura": ["Future of Work"],
    "APLYiD": ["Cybersecurity", "FinTech / Insurance"],
    "Awell Health": ["Health"],
    "Beams": ["Future of Work"],
    "Belong": ["FinTech / Insurance"],
    "Bitskout": ["Future of Work"],
    "Borderless": ["RegTech/Gov/Legal", "Future of Work"],
    "BricksAI": ["Dev Tools / Cloud"],
    "Cogna": ["Dev Tools / Cloud"],
    "Connected": ["Dev Tools / Cloud"],
    "Correcto": ["Future of Work"],
    "Cred Investments": ["FinTech / Insurance"],
    "Devo": ["Consumer", "Logistics / Supply Chain"],
    "digital shadows": ["Cybersecurity"],
    "Dudechem": ["Climate / Sustainability", "Logistics / Supply Chain"],
    "Ecrebo": ["Consumer", "Data & Analytics"],
    "Edgify": ["Consumer", "Deeptech / Robotics / AR/VR"],
    "Elliptic": ["Web3 / Crypto", "FinTech / Insurance"],
    "Fortify Ai": ["Cybersecurity"],
    "Geosurge": ["Data & Analytics"],
    "glofox": ["Consumer"],
    "GoAutonomous": ["Consumer"],
    "Gravel": ["Data & Analytics"],
    "HallTech": ["Deeptech / Robotics / AR/VR"],
    "Hijack Bio": ["BioTech"],
    "Homesearch": ["PropTech"],
    "Hurr": ["Consumer", "Climate / Sustainability"],
    "Hypercritical": ["Dev Tools / Cloud", "Deeptech / Robotics / AR/VR"],
    "inrupt": ["Dev Tools / Cloud", "Cybersecurity"],
    "Interact Software": ["Future of Work"],
    "Intigriti": ["Cybersecurity"],
    "iSize": ["Gaming / Media / Entertainment", "Deeptech / Robotics / AR/VR"],
    "Jolt": ["Future of Work"],
    "Kleene": ["Data & Analytics"],
    "Luna": ["Health", "Consumer"],
    "Mention Me": ["Consumer"],
    "Microsoft Swiftkey": ["Consumer"],
    "Movable Voice": ["Future of Work"],
    "Natterbox": ["Future of Work"],
    "Ometria": ["Data & Analytics", "Consumer"],
    "OpenR": ["Data & Analytics", "Consumer"],
    "Pendula": ["Future of Work"],
    "Poindexter Labs": ["Dev Tools / Cloud"],
    "Prima Mente": ["Health", "BioTech"],
    "Rekord": ["Data & Analytics"],
    "Resolutiion": ["Future of Work"],
    "The Safeguarding Company": ["RegTech/Gov/Legal"],
    "Token": ["FinTech / Insurance"],
    "ValueBlue": ["Dev Tools / Cloud"],
    "Verna": ["Climate / Sustainability", "PropTech"],
    "Visible": ["Health"],
    "Volunteero": ["Future of Work"],
    "Wazoku": ["Future of Work"],
    "XYZ Reality": ["PropTech", "Deeptech / Robotics / AR/VR"],
    "Zapnito": ["Future of Work"],
    "Zynstra": ["Consumer"],
}


def cards(path, max_pages=40):
    out = []
    for p in range(1, max_pages + 1):
        url = f"{BASE}{path}" + ("" if p == 1 else f"page/{p}/") + "?_=1"
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
        except requests.RequestException:
            r = None
        if r is None or r.status_code == 404:
            break  # past the last archive page
        soup = BeautifulSoup(fetch_response(url).text if r.status_code != 200 else r.text, "html.parser")
        page = soup.select(".company-card article.card-item")
        if not page:
            break
        out += page
    return out


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    status_of = {}
    for term in ("exited", "current"):
        for art in cards(f"/portfolio-status/{term}/"):
            name = clean(art.get("aria-label"))
            if name:
                status_of.setdefault(name.lower(), term.capitalize())
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for art in cards("/portfolio/"):
        title = art.select_one(".card-item-title")
        name = clean(art.get("aria-label")) or clean(title.get_text(" ", strip=True) if title else None)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        ex = art.select_one(".card-itemExcerpt")
        desc = clean(ex.get_text(" ", strip=True)) if ex else None
        a = art.find("a", href=True)
        url = clean_url(a["href"]) if a and "octopusventures.com" not in a["href"] else None
        sectors = [SECTORS[c] for c in art.get("class") or [] if c in SECTORS]
        # "Pre-seed" is Octopus's pre-seed programme filter, i.e. an entry stage, not a sector
        stage = "Pre-Seed" if "Pre-seed" in sectors else None
        sectors = [x for x in sectors if x != "Pre-seed"]
        raw = status_of.get(name.lower())
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": url,
            "status": STATUS.get((raw or "").lower()),
            "site_status": raw,
            "stage": stage,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")
    print("  exited:", sum(1 for x in out if x["status"] == "acquired"))


if __name__ == "__main__":
    main()
