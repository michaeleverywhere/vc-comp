#!/usr/bin/env python3
"""Elaia portfolio scraper -> elaia_companies.json
Source: https://elaia.com/portfolio — Next.js front end over Elaia's own
Payload CMS; the portfolio archive is rendered from the `portfolio`
collection, read here from the site's public REST endpoint
(https://elaia.com/api/portfolio). Per company: name, companyStatus
(active / exit), sector(s), geography (country), Elaia team, website, bio
(rich text -> description) and entrepreneurs (founders). No funding round or
investment year is published.
Status: active -> active; exit -> acquired (raw kept in site_status).
"""
import json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://elaia.com/portfolio"
API = "https://elaia.com/api/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "elaia_companies.json")
PRIMARY = "Elaia"
SECTOR_TAG_MAP = {
    "adtech": ["Gaming / Media / Entertainment"], "biotech & healthcare": ["BioTech", "Health"],
    "cybersecurity": ["Cybersecurity"], "energy & climate": ["Climate / Sustainability"],
    "fintech": ["FinTech / Insurance"], "infra & devops": ["Dev Tools / Cloud"],
    "new computing": ["Deeptech / Robotics / AR/VR"], "robotics & automation": ["Deeptech / Robotics / AR/VR"],
}
STATUS = {"active": "active", "exit": "acquired", "exited": "acquired"}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "AGNITiO": ["Cybersecurity", "RegTech/Gov/Legal"],
    "Allmyapps": ["Consumer", "Dev Tools / Cloud"],
    "Azalea Vision": ["Health", "Deeptech / Robotics / AR/VR"],
    "Beloy": ["FinTech / Insurance", "Consumer"],
    "Case Law Analytics": ["RegTech/Gov/Legal", "Data & Analytics"],
    "Criteo": ["Gaming / Media / Entertainment", "Data & Analytics"],
    "Cryptosense": ["Cybersecurity"],
    "Enso Security": ["Cybersecurity", "Dev Tools / Cloud"],
    "Golaem": ["Gaming / Media / Entertainment"],
    "H - AI": ["Dev Tools / Cloud", "Future of Work"],
    "Hyvibe": ["Gaming / Media / Entertainment", "Consumer"],
    "Jware Technologies": ["Dev Tools / Cloud"],
    "Kheops": ["Logistics / Supply Chain"],
    "Linkup": ["Dev Tools / Cloud"],
    "Mensia technologies": ["Health"],
    "METRIXWARE": ["Dev Tools / Cloud"],
    "NTRglobal": ["Dev Tools / Cloud", "Cybersecurity"],
    "Olympe.legal": ["RegTech/Gov/Legal"],
    "Ornis": ["Dev Tools / Cloud"],
    "Power Design Technologies": ["Deeptech / Robotics / AR/VR", "Climate / Sustainability"],
    "Quortex": ["Dev Tools / Cloud", "Gaming / Media / Entertainment"],
    "SandboxAQ": ["Deeptech / Robotics / AR/VR", "Cybersecurity", "BioTech"],
    "Verra": ["Data & Analytics"],
    "ZenChef": ["Consumer", "Future of Work"],
}


def rich_text(node):
    if not isinstance(node, dict):
        return ""
    if node.get("type") == "text":
        return node.get("text") or ""
    parts = [rich_text(c) for c in node.get("children") or []]
    sep = " " if node.get("type") in ("root",) else ""
    return sep.join(p for p in parts if p)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    docs, page = [], 1
    while True:
        d = fetch(f"{API}?limit=100&page={page}&depth=1&sort=name", as_json=True)
        docs += d.get("docs") or []
        if not d.get("hasNextPage"):
            break
        page += 1
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for x in docs:
        name = clean(x.get("name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        bio = x.get("bio") or {}
        desc = clean(rich_text(bio.get("root") if isinstance(bio, dict) else None))
        if desc and len(desc) < 3:
            desc = None  # stub bios (e.g. a lone "S") are not descriptions
        # The site files Enso Security under its acquirer's name ("Snyk");
        # its own bio says "Enso ... Acquired by Snyk".
        if name == "Snyk" and desc and desc.startswith("Enso "):
            name = "Enso Security"
        sectors = [clean(s.get("title")) for s in x.get("sector") or [] if isinstance(s, dict) and clean(s.get("title"))]
        geo = [clean(g.get("title")) for g in x.get("geography") or [] if isinstance(g, dict) and clean(g.get("title"))]
        raw = clean(x.get("companyStatus"))
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url((x.get("website") or {}).get("url")),
            "company_profile_url": f"https://elaia.com/portfolio/{x['slug']}" if x.get("slug") else None,
            "status": STATUS.get((raw or "").lower()),
            "site_status": raw,
            "location": ", ".join(geo) or None,
            "founders": [clean(e.get("name")) for e in x.get("entrepreneurs") or [] if clean(e.get("name"))],
            "partners": [clean(t.get("name")) for t in x.get("team") or [] if isinstance(t, dict) and clean(t.get("name"))],
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
    for k in ("description", "company_url", "status", "location", "founders", "partners", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
