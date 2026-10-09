#!/usr/bin/env python3
"""Giant Leap portfolio scraper -> giantleap_companies.json
Source: https://www.giantleap.com.au/portfolio — Webflow CMS list (Finsweet
filters), fully server-rendered. Each card links to the company website and
carries the impact category (Climate / Health / People), name (h3) and a
one-line description. No stage, location, year or status is published.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.giantleap.com.au/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "giantleap_companies.json")
PRIMARY = "Giant Leap"
SECTOR_TAG_MAP = {"climate": ["Climate / Sustainability"], "health": ["Health"]}

# Hand-reviewed tags (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Academy Xi": ["Future of Work"],
    "Amber": ["Climate / Sustainability", "Consumer"],
    "Applied": ["Future of Work"],
    "Change Foods": ["CPG", "Climate / Sustainability", "BioTech"],
    "Clean Slate": ["Health"],
    "Conserving Beauty": ["CPG", "Climate / Sustainability"],
    "Coviu": ["Health"],
    "Driven": ["Health"],
    "Evrnu": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "FlyORO": ["Climate / Sustainability", "Transportation / Mobility", "Logistics / Supply Chain"],
    "Foremind": ["Future of Work", "Health"],
    "Full Cycle": ["Climate / Sustainability"],
    "Future Super": ["FinTech / Insurance", "Climate / Sustainability"],
    "GlamCorner": ["Consumer", "Climate / Sustainability"],
    "Goterra": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Great Wrap": ["Climate / Sustainability", "Logistics / Supply Chain"],
    "HEX": ["Future of Work"],
    "Kernl": ["Health", "Future of Work"],
    "Like Family": ["Health", "Consumer"],
    "Loop+": ["Health", "Deeptech / Robotics / AR/VR"],
    "Mindset": ["Health"],
    "Modo": ["Health", "Consumer"],
    "MoreGoodDays": ["Health"],
    "Music Health": ["Health"],
    "Ovum": ["Health", "Data & Analytics"],
    "Perx Health": ["Health"],
    "Project Indi": ["Health", "Consumer"],
    "Seer Medical": ["Health"],
    "Sendle": ["Logistics / Supply Chain", "Climate / Sustainability"],
    "SPEC Toolbox": ["Climate / Sustainability", "PropTech"],
    "Switch Automation": ["PropTech", "Climate / Sustainability"],
    "Swoop Aero": ["Deeptech / Robotics / AR/VR", "Logistics / Supply Chain", "Health"],
    "Trace": ["Climate / Sustainability", "Data & Analytics"],
    "Who Gives a Crap": ["CPG", "Climate / Sustainability"],
    "WORK 180": ["Future of Work"],
    "Your Grocer": ["Consumer", "Logistics / Supply Chain"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for a in soup.select("a.portfolio_item"):
        h = a.select_one("h3")
        name = clean(h.get_text(" ")) if h else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        p = a.select_one("p")
        desc = clean(p.get_text(" ")) if p else None
        sectors = [clean(x.get_text(" ")) for x in a.select('[fs-cmsfilter-field="category"]') if clean(x.get_text(" "))]
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a.get("href")),
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
    for k in ("description", "company_url", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
