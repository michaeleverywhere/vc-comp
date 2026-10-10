#!/usr/bin/env python3
"""Samsung Next portfolio scraper -> samsungnext_companies.json
Source: https://www.samsungnext.com/portfolio — Webflow page that renders
100 cards server-side and loads the full list (352 at first scrape) from a
static JSON on the Webflow CDN (`..._pf-companies-v2.json`, fields n=name,
s=sector, w=website). The JSON URL is discovered from the page each run.
The firm site has no descriptions, stages, dates or statuses; empty
descriptions are filled from company websites / Wikidata by
scripts/fill_descriptions_web.py and carried forward on re-runs.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, carry_forward_descriptions, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://www.samsungnext.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "samsungnext_companies.json")
PRIMARY = "Samsung Next"
SECTOR_TAG_MAP = {"health tech": ["Health"], "robotics": ["Deeptech / Robotics / AR/VR"], "frontier": ["Deeptech / Robotics / AR/VR"]}
TAG_OVERRIDES = {}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    page = fetch(SOURCE_URL)
    m = re.search(r"https://cdn\.prod\.website-files\.com/[^'\"\s]+_pf-companies-v2\.json", page) or \
        re.search(r"https://cdn\.prod\.website-files\.com/[^'\"\s]+_pf-companies\.json", page)
    if not m:
        sys.exit("portfolio JSON URL not found on page")
    rows = fetch(m.group(0), as_json=True)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for o in rows:
        name = clean(o.get("n"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        sector = clean(o.get("s"))
        out.append({
            "company_name": name,
            "description": None,
            "company_url": clean_url(o.get("w")),
            "sector": sector,
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "data_url": m.group(0),
            "scraped_at": scraped_at,
        })
    if limit:
        out = out[:limit]
    carry_forward_descriptions(out, OUT)
    for r in out:
        secs = [r["sector"]] if r.get("sector") and r["sector"] not in ("AI", "Others", "Services") else []
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description") or "", secs, SECTOR_TAG_MAP)
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "sector", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
