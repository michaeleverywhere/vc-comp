#!/usr/bin/env python3
"""Folklore Ventures portfolio scraper -> folklore_companies.json
Source: https://www.folklore.vc/companies — Webflow CMS list, fully
server-rendered. Each card links to the company website and carries the
name (h3), one-line description, display domain and an optional label
(Acquired / Exited / IPO). No stage, location or investment year is
published, so those stay blank.
Status: Acquired / Exited -> acquired; IPO left blank (not an acquisition);
raw label kept in site_status.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.folklore.vc/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "folklore_companies.json")
PRIMARY = "Folklore Ventures"
STATUS = {"acquired": "acquired", "exited": "acquired"}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Auror": ["Cybersecurity", "Data & Analytics"],
    "Featureflow": ["Dev Tools / Cloud"],
    "Forever Network": ["Gaming / Media / Entertainment"],
    "HealthMatch": ["Health", "BioTech"],
    "Kry10": ["Cybersecurity", "Deeptech / Robotics / AR/VR"],
    "Lived": ["Health", "Consumer"],
    "Mentorloop": ["Future of Work"],
    "Octopusbot": ["Data & Analytics", "Logistics / Supply Chain"],
    "oslo.ai": ["Dev Tools / Cloud"],
    "ProductEngine": ["Future of Work"],
    "Wonde": ["Consumer"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select(".mansory-item.w-dyn-item"):
        h = it.select_one("h3")
        name = clean(h.get_text(" ")) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        p = it.select_one("p")
        desc = clean(p.get_text(" ")) if p else None
        a = it.select_one("a[href^=http]")
        label = next((clean(l.get_text(" ")) for l in it.select(".investment-label")
                      if "w-condition-invisible" not in (l.get("class") or []) and clean(l.get_text(" "))), None)
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a else None,
            "status": STATUS.get((label or "").lower()),
            "site_status": label,
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, None)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
