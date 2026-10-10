#!/usr/bin/env python3
"""OMERS Ventures portfolio scraper -> omers_companies.json
Source: https://www.omersventures.com/companies — Next.js page whose RSC
payload embeds the Contentful "portfolio" entries: title, industry (OMERS
theme), region (Canada / US / Europe), websiteUrl and exited (Current vs
Former). The firm site carries no descriptions; empty descriptions are
filled from the companies' own websites / Wikidata by
scripts/fill_descriptions_web.py and carried forward on re-runs.
status: Current -> active; Former (exited) is kept as site_status only
(the site does not say acquired vs listed). location is the region only when
it is a country (Canada / United States); "Europe" stays in region.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, carry_forward_descriptions, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://www.omersventures.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "omers_companies.json")
PRIMARY = "OMERS Ventures"
COUNTRY = {"Canada": "Canada", "US": "United States"}
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "consumer": ["Consumer"], "deep tech": ["Deeptech / Robotics / AR/VR"],
    "infrastructure software": ["Dev Tools / Cloud"], "sovereignty": ["RegTech/Gov/Legal"],
}
TAG_OVERRIDES = {  # hand-reviewed (no LLM)
    "Cohere": ["Data & Analytics", "Dev Tools / Cloud"],
    "Shopify": ["Consumer", "FinTech / Insurance"],
    "Snyk": ["Cybersecurity", "Dev Tools / Cloud"],
    "Embark Truck": ["Transportation / Mobility", "Logistics / Supply Chain"],
    "Waabi": ["Transportation / Mobility", "Deeptech / Robotics / AR/VR"],
    "Xanadu": ["Deeptech / Robotics / AR/VR"],
    "Ranovus": ["Deeptech / Robotics / AR/VR"],
    "Digital Currency Group": ["Web3 / Crypto"],
    "Hopper": ["Consumer"],
    "Busbud": ["Consumer", "Transportation / Mobility"],
    "Rover": ["Consumer"],
    "Wattpad": ["Gaming / Media / Entertainment", "Consumer"],
    "Medal.tv": ["Gaming / Media / Entertainment", "Consumer"],
    "Felix & Paul": ["Gaming / Media / Entertainment", "Deeptech / Robotics / AR/VR"],
    "NAAMA Studios": ["Gaming / Media / Entertainment"],
    "DuckDuckGo": ["Consumer", "Cybersecurity"],
    "Deep Sky": ["Climate / Sustainability"],
    "Crux": ["Climate / Sustainability", "FinTech / Insurance"],
    "Manifest Climate": ["Climate / Sustainability", "Data & Analytics"],
    "FirstVet": ["Health", "Consumer"],
    "League": ["Health"],
    "HelloSelf": ["Health", "Consumer"],
    "Muse by Interaxon": ["Health", "Consumer"],
    "Contentful": ["Dev Tools / Cloud"],
    "Cerbos": ["Cybersecurity", "Dev Tools / Cloud"],
    "Arize": ["Dev Tools / Cloud", "Data & Analytics"],
    "Dominion Dynamics": ["RegTech/Gov/Legal", "Deeptech / Robotics / AR/VR"],
    "Daedal Systems": ["RegTech/Gov/Legal", "Deeptech / Robotics / AR/VR"],
    "ClearEstate": ["FinTech / Insurance"],
    "Occupier": ["PropTech"],
    "Lick Home": ["Consumer", "PropTech"],
    "Wefox": ["FinTech / Insurance"],
    "Clearcover": ["FinTech / Insurance"],
    "Jobber": ["Future of Work"],
    "WorkRamp": ["Future of Work"],
    "Vidyard": ["Gaming / Media / Entertainment", "Future of Work"],
    "Hootsuite": ["Gaming / Media / Entertainment", "Future of Work"],
    "D2L": ["Future of Work"],
    "Klipfolio": ["Data & Analytics"],
    "Crunchbase": ["Data & Analytics"],
    "Altana Technologies": ["Logistics / Supply Chain", "Data & Analytics"],
    "Deliverect": ["Consumer", "Logistics / Supply Chain"],
    "TouchBistro": ["FinTech / Insurance", "Consumer"],
    "Password Box": ["Cybersecurity", "Consumer"],
    "Solink": ["Cybersecurity", "Data & Analytics"],
    "Agile Analog": ["Deeptech / Robotics / AR/VR"],
}


def _rsc_text(html):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    return "".join(json.loads('"' + c + '"') for c in chunks)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    txt = _rsc_text(fetch(SOURCE_URL))
    scraped_at = datetime.now(timezone.utc).isoformat()
    dec = json.JSONDecoder()
    seen, out = set(), []
    for m in re.finditer(r'\{"id":"[^"]+","contentType":"portfolio",', txt):
        o, _ = dec.raw_decode(txt[m.start():])
        if o["id"] in seen:
            continue
        seen.add(o["id"])
        name = clean(o.get("title") or o.get("entryTitle"))
        if not name:
            continue
        industry = clean(o.get("industry"))
        region = clean(o.get("region"))
        exited = o.get("exited")
        out.append({
            "company_name": name,
            "description": None,
            "company_url": clean_url(o.get("websiteUrl")),
            "industry": industry,
            "region": region,
            "location": COUNTRY.get(region),
            "site_status": "Former" if exited else ("Current" if exited is False else None),
            "status": "active" if exited is False else None,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    if limit:
        out = out[:limit]
    carry_forward_descriptions(out, OUT)
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description") or "", [r["industry"]] if r.get("industry") else [], SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "industry", "location", "status", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
