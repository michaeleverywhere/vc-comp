#!/usr/bin/env python3
"""byFounders portfolio scraper -> byfounders_companies.json
Source: https://byfounders.vc/portfolio — server-rendered TanStack app. The
visible grid shows name, website and month invested; the page's own
serialized router state ($R[n]={id:...,externalId:...} objects) carries the
full record per company: name, aliases (former names), announced flag,
vertical, current stage, entryStage, initialDateInvested, geo and href.
Only announced companies are kept — unannounced ones render as "Stealth" on
the site and are deliberately not exposed here.
stage = entryStage (round at byFounders' entry); current stage kept raw.
Status: current stage Exit / Acquired -> acquired; otherwise active (listed
in the live portfolio grid).
No descriptions are published.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, year_of, stage_label, clean_url, carry_forward_descriptions, apply_tag_overrides

SOURCE_URL = "https://byfounders.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "byfounders_companies.json")
PRIMARY = "byFounders"
SECTOR_TAG_MAP = {
    "deep tech": ["Deeptech / Robotics / AR/VR"], "energy & climate": ["Climate / Sustainability"],
    "health": ["Health"], "consumer": ["Consumer"], "consumer saas": ["Consumer"],
    "dev & design tools": ["Dev Tools / Cloud"], "cloud infrastructure": ["Dev Tools / Cloud"],
    "fintech": ["FinTech / Insurance"], "techbio & bio": ["BioTech"], "gaming": ["Gaming / Media / Entertainment"],
    "media": ["Gaming / Media / Entertainment"], "sales/marketing/cs": ["Future of Work"],
    "industry 4.0 & iot": ["Deeptech / Robotics / AR/VR"], "cybersecurity": ["Cybersecurity"],
    "spacetech": ["Deeptech / Robotics / AR/VR"], "robotics": ["Deeptech / Robotics / AR/VR"],
    "electronics": ["Deeptech / Robotics / AR/VR"], "b2b saas": ["Future of Work"],
    "enterprise saas": ["Future of Work"],
}
OBJ = re.compile(r'\$R\[\d+\]=\{(id:"[^"]*",externalId:(?:[^{}\[\]]|\[[^\]]*\])*)\}')


def parse(html):
    out = []
    for o in OBJ.findall(html):
        o = re.sub(r"\$R\[\d+\]=", "", o)
        j = re.sub(r'(?<=[{,])(\w+):', r'"\1":', "{" + o + "}").replace(":!0", ":true").replace(":!1", ":false")
        try:
            out.append(json.loads(j))
        except json.JSONDecodeError:
            continue
    return out


# Hand-reviewed tag fixes (judgment pass, no LLM): keyword tagger substring
# false positives (e.g. "rent" in "current", "llm" in "fulfillment") and
# clearly wrong labels. Applied after keyword tagging.
TAG_OVERRIDES = {
    "Cobalt": ["Cybersecurity", "Transportation / Mobility"],
    "Lucinity": ["FinTech / Insurance"],
    "Outfunnel": ["Future of Work"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for r in sorted(parse(html), key=lambda x: x.get("externalId") or 0):
        name = clean(r.get("name"))
        if not name or not r.get("announced") or name.lower() in seen:
            continue
        seen.add(name.lower())
        cur = clean(r.get("stage"))
        href = r.get("href")
        if href and not href.startswith("http"):
            href = "https://" + href
        sectors = [r["vertical"]] if r.get("vertical") else []
        out.append({
            "company_name": name,
            "former_names": r.get("aliases") or [],
            "description": None,
            "company_url": clean_url(href),
            "status": "acquired" if (cur or "").lower() in ("exit", "acquired") else "active",
            "current_stage": cur,
            "entry_stage": clean(r.get("entryStage")),
            "stage": stage_label(r.get("entryStage")),
            "initial_date_invested": r.get("initialDateInvested"),
            "first_invested": year_of(r.get("initialDateInvested")),
            "location": clean(r.get("geo")),
            "sectors": sectors,
            "everywhere_tags": tags_for(name, None, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    for r in carry_forward_descriptions(out, OUT):
        r["everywhere_tags"] = tags_for(r["company_name"], r["description"], r.get("sectors"), SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("company_url", "status", "stage", "first_invested", "location", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
