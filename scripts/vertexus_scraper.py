#!/usr/bin/env python3
"""Vertex Ventures US portfolio scraper -> vertexus_companies.json
Source: https://vvus.com/portfolio/ — Gatsby + Storyblok site. The portfolio
grid is fed by a Gatsby static query; the scraper reads
/page-data/portfolio/page-data.json, follows its staticQueryHashes to
/page-data/sq/d/<hash>.json and picks the one holding `projects.edges`
(each node's `content` is the Storyblok `data_project` JSON).
Fields: project_name, project_description, project_socials (website),
project_category (Active / Recent / Exited + sector labels),
project_acquiredBy, project_founders (names only).
Exited or a published acquirer -> acquired; Active -> active.
No rounds, dates or locations are published.
"""
import json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

BASE = "https://vvus.com"
SOURCE_URL = BASE + "/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "vertexus_companies.json")
PRIMARY = "Vertex Ventures US"
STATUS_LABELS = {"active", "recent", "exited"}
SECTOR_TAG_MAP = {
    "developer tools": ["Dev Tools / Cloud"], "infrastructure": ["Dev Tools / Cloud"], "data": ["Data & Analytics"],
    "security": ["Cybersecurity"], "fintech": ["FinTech / Insurance"], "deep tech": ["Deeptech / Robotics / AR/VR"],
    "open-source": ["Dev Tools / Cloud"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Recce": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "OLIX": [
        "Deeptech / Robotics / AR/VR",
        "Dev Tools / Cloud"
    ],
    "SWARM Biotactics": [
        "Deeptech / Robotics / AR/VR",
        "RegTech/Gov/Legal"
    ],
    "Riley AI": [
        "Data & Analytics",
        "Future of Work"
    ],
    "Northflank": [
        "Dev Tools / Cloud"
    ],
    "Onshore": [
        "FinTech / Insurance",
        "RegTech/Gov/Legal"
    ],
    "Clearpol": [
        "Health"
    ],
    "LightBeam": [
        "Cybersecurity",
        "RegTech/Gov/Legal"
    ],
    "Cloud Academy": [
        "Future of Work",
        "Dev Tools / Cloud"
    ],
    "SpaceIQ": [
        "Future of Work",
        "PropTech"
    ],
    "ZEPL": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Quilt Data": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Docker": [
        "Dev Tools / Cloud"
    ],
    "Vintra": [
        "Data & Analytics",
        "Cybersecurity"
    ],
    "Testlio": [
        "Dev Tools / Cloud"
    ],
    "DOR": [
        "Data & Analytics",
        "Consumer"
    ],
    "Fyde": [
        "Cybersecurity"
    ],
    "Tulip": [
        "Deeptech / Robotics / AR/VR",
        "Data & Analytics"
    ],
    "Juno": [
        "PropTech",
        "Climate / Sustainability"
    ],
    "Elotl": [
        "Dev Tools / Cloud"
    ],
    "Pronto": [
        "Future of Work"
    ],
    "Orkes": [
        "Dev Tools / Cloud"
    ],
    "LeaseLock": [
        "FinTech / Insurance",
        "PropTech"
    ],
    "Experify": [
        "Consumer"
    ],
    "Evisort": [
        "RegTech/Gov/Legal",
        "Future of Work"
    ],
    "VGS": [
        "Cybersecurity",
        "FinTech / Insurance"
    ],
    "Vividly": [
        "Data & Analytics",
        "CPG"
    ],
    "Cosmonic": [
        "Dev Tools / Cloud"
    ],
    "Broker Buddha": [
        "FinTech / Insurance"
    ],
}


def load_projects():
    pd = fetch(BASE + "/page-data/portfolio/page-data.json", as_json=True)
    for h in pd.get("staticQueryHashes", []):
        try:
            sq = fetch(f"{BASE}/page-data/sq/d/{h}.json", as_json=True)
        except Exception:
            continue
        edges = ((sq.get("data") or {}).get("projects") or {}).get("edges")
        if edges:
            return edges
    sys.exit("projects static query not found")


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for e in load_projects():
        node = e.get("node") or {}
        try:
            c = json.loads(node.get("content") or "{}")
        except ValueError:
            continue
        name = clean(c.get("project_name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cats = [clean(x) for x in (c.get("project_category") or []) if clean(x)]
        labels = {x.lower() for x in cats}
        sectors = [x for x in cats if x.lower() not in STATUS_LABELS]
        desc = clean(c.get("project_description"))
        site = next((s.get("url") for s in (c.get("project_socials") or []) if s.get("type") == "website" and s.get("url")), None)
        acquirer = clean(c.get("project_acquiredBy"))
        status = "acquired" if (acquirer or "exited" in labels) else ("active" if labels & {"active", "recent"} else None)
        founders = [clean(f.get("title")) for f in (c.get("project_founders") or []) if clean(f.get("title"))]
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(site) if site else None,
            "status": status,
            "site_status": next((x for x in cats if x.lower() in STATUS_LABELS), None),
            "acquirer": acquirer,
            "founders": founders,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc or "", sectors, SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "status", "acquirer", "founders", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
