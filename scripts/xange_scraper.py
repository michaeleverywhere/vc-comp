#!/usr/bin/env python3
"""XAnge portfolio scraper -> xange_companies.json
Source: https://www.xange.vc/portfolio — Next.js site backed by XAnge's own
Prismic CMS (repository "xange"); the portfolio grid is rendered from its
`startup` documents, so this reads the same documents from the public
Prismic content API (https://xange.cdn.prismic.io/api/v2, master ref).
Per startup: name, website, investment_date, locations, sectors, XAnge
investors (team members), status (Active / Exited), fund, and the page
description. Linked sector/location/status/team documents are resolved by id.
Status: Active -> active, Exited -> acquired (raw kept in site_status).
"""
import json, os, sys
from datetime import datetime, timezone
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, year_of, clean_url, apply_tag_overrides

SOURCE_URL = "https://www.xange.vc/portfolio"
API = "https://xange.cdn.prismic.io/api/v2"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "xange_companies.json")
PRIMARY = "XAnge"
SECTOR_TAG_MAP = {
    "fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"], "edtech": ["Future of Work"],
    "healthtech": ["Health"], "legaltech": ["RegTech/Gov/Legal"], "hr": ["Future of Work"],
    "logistics": ["Logistics / Supply Chain"], "mobility": ["Transportation / Mobility"],
    "proptech": ["PropTech"], "cybersecurity": ["Cybersecurity"], "aerospace": ["Deeptech / Robotics / AR/VR"],
    "climate": ["Climate / Sustainability"], "energy": ["Climate / Sustainability"],
    "retail": ["Consumer"], "gaming": ["Gaming / Media / Entertainment"], "media": ["Gaming / Media / Entertainment"],
    "web3": ["Web3 / Crypto"], "blockchain": ["Web3 / Crypto"], "robotics": ["Deeptech / Robotics / AR/VR"],
    "foodtech": ["CPG"], "food": ["CPG"], "data service": ["Data & Analytics"], "dev tools": ["Dev Tools / Cloud"],
    "climatetech": ["Climate / Sustainability"], "clean tech": ["Climate / Sustainability"],
    "energy management": ["Climate / Sustainability"], "e-commerce": ["Consumer"], "biotech": ["BioTech"],
    "prop tech": ["PropTech"], "smart cities": ["PropTech"], "music tech": ["Gaming / Media / Entertainment"],
    "adtech": ["Gaming / Media / Entertainment"], "semiconductors": ["Deeptech / Robotics / AR/VR"],
    "3d printing": ["Deeptech / Robotics / AR/VR"], "hardware and materials": ["Deeptech / Robotics / AR/VR"],
    "cloud computing & infrastructure": ["Dev Tools / Cloud"], "network infrastructure": ["Dev Tools / Cloud"],
    "health hardware": ["Health"], "civictech": ["RegTech/Gov/Legal"], "beauty tech": ["Consumer"],
    "traveltech & hospitality": ["Consumer"], "b2b saas": ["Future of Work"],
}


def docs(ref, doc_type):
    out, page = [], 1
    while True:
        q = quote(f'[[at(document.type,"{doc_type}")]]')
        d = fetch(f"{API}/documents/search?ref={ref}&q={q}&pageSize=100&page={page}&lang=*", as_json=True)
        out += d["results"]
        if page >= d.get("total_pages", 1):
            return out
        page += 1


def text_of(rich):
    return clean(" ".join(b.get("text", "") for b in rich or [] if isinstance(b, dict))) if rich else None


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Bigblue": ["Logistics / Supply Chain", "Consumer"],
    "Currency Cloud": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Epigene Labs": ["BioTech", "Data & Analytics"],
    "Flink": ["Consumer", "Logistics / Supply Chain"],
    "Homaio": ["Climate / Sustainability", "FinTech / Insurance"],
    "Lydia": ["FinTech / Insurance"],
    "Mister Spex": ["Consumer", "CPG"],
    "Promus": ["Logistics / Supply Chain", "CPG"],
    "Shine": ["FinTech / Insurance"],
    "Ubaq": ["RegTech/Gov/Legal"],
    "Valuecase": ["Future of Work"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    ref = next(r["ref"] for r in fetch(API, as_json=True)["refs"] if r.get("isMasterRef"))
    scraped_at = datetime.now(timezone.utc).isoformat()
    names = {}
    for t in ("sector", "location", "company_status", "fund"):
        for x in docs(ref, t):
            names[x["id"]] = clean(x["data"].get("name"))
    for x in docs(ref, "team_member"):
        names[x["id"]] = clean(f'{x["data"].get("first_name") or ""} {x["data"].get("last_name") or ""}')
    ref_name = lambda v: names.get((v or {}).get("id")) if isinstance(v, dict) else None
    out, seen = [], set()
    for doc in sorted(docs(ref, "startup"), key=lambda x: (x["data"].get("name") or "").lower()):
        d = doc["data"]
        name = clean(d.get("name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = None
        for blk in d.get("page") or []:
            desc = text_of(blk.get("description"))
            if desc:
                break
        sectors = [n for n in (ref_name(s.get("sector")) for s in d.get("sectors") or []) if n]
        locs = [n for n in (ref_name(s.get("location")) for s in d.get("locations") or []) if n]
        team = [n for n in (ref_name(s.get("investor")) for s in d.get("investors") or []) if n]
        funds = [n for n in (ref_name(s.get("fund")) for s in d.get("funds") or []) if n]
        st = ref_name(d.get("status"))
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url((d.get("website") or {}).get("url")),
            "company_profile_url": f"https://www.xange.vc/portfolio/{doc['uid']}" if doc.get("uid") else None,
            "status": {"active": "active", "exited": "acquired"}.get((st or "").lower()),
            "site_status": st,
            "investment_date": d.get("investment_date"),
            "first_invested": year_of(d.get("investment_date")),
            "location": ", ".join(locs) or None,
            "sectors": sectors,
            "xange_investors": team,
            "funds": funds,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "first_invested", "location", "sectors", "xange_investors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
