#!/usr/bin/env python3
"""Ventures Platform portfolio scraper -> venturesplatform_companies.json
Source: https://www.venturesplatform.com/portfolio — Webflow CMS list
(server-rendered, Finsweet filters). Each card's dropdown carries the logo
(img alt = company name), a one-line summary, website, long description,
Founders, Industry, Initial Investment (entry round) and Status
(Active / Inactive / Exited). The per-company /portfolio-companies/ pages are
empty templates, so everything comes from the listing.
Initial Investment (Pre-Seed / Seed / Series A ...) -> stage (published
entry round). Status: Active -> active; Exited -> acquired; Inactive -> blank
(raw label kept in site_status).
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, stage_label, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.venturesplatform.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "venturesplatform_companies.json")
PRIMARY = "Ventures Platform"
STATUS = {"active": "active", "exited": "acquired"}
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "healthtech": ["Health"], "health": ["Health"],
    "edtech": ["Future of Work"], "agritech": ["Climate / Sustainability", "CPG"],
    "logistics": ["Logistics / Supply Chain"], "mobility": ["Transportation / Mobility"],
    "insurtech": ["FinTech / Insurance"], "proptech": ["PropTech"], "cleantech": ["Climate / Sustainability"],
    "energy": ["Climate / Sustainability"], "e-commerce": ["Consumer"], "commerce": ["Consumer"],
    "hr tech": ["Future of Work"], "hrtech": ["Future of Work"], "legaltech": ["RegTech/Gov/Legal"],
    "cybersecurity": ["Cybersecurity"], "media": ["Gaming / Media / Entertainment"],
    "blockchain": ["Web3 / Crypto"], "crypto": ["Web3 / Crypto"], "data": ["Data & Analytics"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Bitnob": [
        "FinTech / Insurance",
        "Web3 / Crypto"
    ],
    "Bloc": [
        "FinTech / Insurance",
        "Dev Tools / Cloud"
    ],
    "Brass": [
        "FinTech / Insurance"
    ],
    "BridgeCard": [
        "FinTech / Insurance",
        "Dev Tools / Cloud"
    ],
    "Caantin": [
        "Data & Analytics"
    ],
    "Catlog": [
        "FinTech / Insurance",
        "Consumer"
    ],
    "Chargel": [
        "Logistics / Supply Chain"
    ],
    "ChowCentral": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "Co-Buildit": [
        "FinTech / Insurance",
        "PropTech"
    ],
    "Connected Analytics": [
        "FinTech / Insurance",
        "Data & Analytics"
    ],
    "Cova": [
        "FinTech / Insurance"
    ],
    "Credable": [
        "FinTech / Insurance",
        "Dev Tools / Cloud"
    ],
    "Credit Clan": [
        "FinTech / Insurance"
    ],
    "Crowdforce": [
        "FinTech / Insurance"
    ],
    "Cybervergent": [
        "Cybersecurity",
        "RegTech/Gov/Legal"
    ],
    "Ebanqo Inc.": [
        "Future of Work"
    ],
    "Engage": [
        "Future of Work"
    ],
    "Fez": [
        "Logistics / Supply Chain"
    ],
    "Fluna": [
        "FinTech / Insurance",
        "Logistics / Supply Chain"
    ],
    "Frain": [
        "Logistics / Supply Chain"
    ],
    "Gerocare": [
        "Health"
    ],
    "Gradely": [
        "Future of Work",
        "Consumer"
    ],
    "HeyFood": [
        "Consumer",
        "Logistics / Supply Chain"
    ],
    "HoneyCoin": [
        "FinTech / Insurance",
        "Web3 / Crypto"
    ],
    "Itana": [
        "RegTech/Gov/Legal",
        "Dev Tools / Cloud"
    ],
    "Karcel": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "Lengo": [
        "Data & Analytics",
        "CPG"
    ],
    "Loomo": [
        "FinTech / Insurance"
    ],
    "Maad": [
        "Logistics / Supply Chain",
        "CPG"
    ],
    "Marketforce": [
        "Consumer",
        "Logistics / Supply Chain",
        "FinTech / Insurance"
    ],
    "MDaaS": [
        "Health"
    ],
    "Mecho Autotech Limited": [
        "Transportation / Mobility"
    ],
    "Migo": [
        "FinTech / Insurance"
    ],
    "Mono": [
        "FinTech / Insurance",
        "Dev Tools / Cloud"
    ],
    "Myka": [
        "FinTech / Insurance"
    ],
    "Notto": [
        "FinTech / Insurance",
        "PropTech"
    ],
    "Omniretail": [
        "Logistics / Supply Chain",
        "FinTech / Insurance",
        "CPG"
    ],
    "Pivo": [
        "FinTech / Insurance",
        "Logistics / Supply Chain"
    ],
    "Plumter": [
        "FinTech / Insurance"
    ],
    "PressOne": [
        "Future of Work"
    ],
    "Printivo": [
        "Consumer"
    ],
    "Quabbly Technologies": [
        "Future of Work",
        "Dev Tools / Cloud"
    ],
    "Raenest": [
        "FinTech / Insurance",
        "Future of Work"
    ],
    "Reliance Health": [
        "Health",
        "FinTech / Insurance"
    ],
    "Remedial Health": [
        "Health",
        "Logistics / Supply Chain",
        "FinTech / Insurance"
    ],
    "Risevest": [
        "FinTech / Insurance"
    ],
    "Rivy": [
        "FinTech / Insurance",
        "Climate / Sustainability"
    ],
    "SaltBox": [
        "Logistics / Supply Chain"
    ],
    "SeamlessHR": [
        "Future of Work",
        "FinTech / Insurance"
    ],
    "Send": [
        "Logistics / Supply Chain"
    ],
    "SendMe Inc.": [
        "Logistics / Supply Chain",
        "CPG"
    ],
    "Shekel Mobility": [
        "Transportation / Mobility",
        "FinTech / Insurance"
    ],
    "Steward": [
        "FinTech / Insurance",
        "Future of Work"
    ],
    "Sudo Africa": [
        "FinTech / Insurance",
        "Dev Tools / Cloud"
    ],
    "Talstack": [
        "Future of Work"
    ],
    "Tambua Health": [
        "Health",
        "Deeptech / Robotics / AR/VR"
    ],
    "Tanél Health": [
        "FinTech / Insurance",
        "Health"
    ],
    "Termii": [
        "Dev Tools / Cloud"
    ],
    "Thrive Agric": [
        "Climate / Sustainability",
        "CPG",
        "FinTech / Insurance"
    ],
    "Tizeti (wifi.com.ng)": [
        "Dev Tools / Cloud"
    ],
    "Traction Apps": [
        "FinTech / Insurance"
    ],
    "Trove Finance": [
        "FinTech / Insurance"
    ],
    "Union54": [
        "FinTech / Insurance",
        "Dev Tools / Cloud"
    ],
    "Vendy": [
        "FinTech / Insurance"
    ],
    "VertoFx": [
        "FinTech / Insurance"
    ],
    "Wealth8": [
        "FinTech / Insurance"
    ],
    "Wesabi": [
        "Consumer",
        "Future of Work"
    ],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select("div.portfolio-collection-item.w-dyn-item"):
        img = it.select_one("img[alt]")
        name = clean(img.get("alt")) if img else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        f = lambda k: next((clean(x.get_text(" ")) for x in it.select(f'[fs-cmsfilter-field="{k}"]') if clean(x.get_text(" "))), None)
        sectors = [clean(x.get_text(" ")) for x in it.select('[fs-cmsfilter-field="sector"]') if clean(x.get_text(" "))]
        summ = it.select_one(".short-summary-holder")
        tagline = clean(summ.get_text(" ")) if summ else None
        dp = it.select_one(".comapny-summary-holder p") or it.select_one(".comapny-summary-holder")
        desc = clean(dp.get_text(" ")) if dp else None
        site = it.select_one(".company-logo-link a[href^=http]")
        fnd = None
        fc = it.select_one(".founders-container .text-size-medium")
        if fc:
            fnd = [clean(x) for x in re.split(r",| & | and ", fc.get_text(" ")) if clean(x)]
        raw_stage = f("stage")
        raw_status = f("status")
        prof = it.select_one("a.link-dont-delete[href]")
        out.append({
            "company_name": name,
            "description": desc or tagline,
            "tagline": tagline,
            "company_url": clean_url(site["href"]) if site else None,
            "company_profile_url": urljoin(SOURCE_URL, prof["href"]) if prof else None,
            "status": STATUS.get((raw_status or "").lower()),
            "site_status": raw_status,
            "stage": stage_label(raw_stage),
            "founders": fnd or [],
            "sectors": sectors,
            "everywhere_tags": tags_for(name, " ".join(x for x in (tagline, desc) if x), sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "stage", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
