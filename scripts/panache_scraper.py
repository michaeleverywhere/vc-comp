#!/usr/bin/env python3
"""Panache Ventures portfolio scraper -> panache_companies.json
Source: https://www.panache.vc/portfolio — Wix site; the portfolio repeater is
server-rendered. Each repeater item carries the company logo linked to the
company website, the company name (h4), a one-line description (p) and the
HQ city (second h4, e.g. "Toronto, ON, Canada"). The site publishes no
stage, investment year or status per company, so those stay blank.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.panache.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "panache_companies.json")
PRIMARY = "Panache Ventures"

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "AgentField": ["Cybersecurity", "Dev Tools / Cloud"],
    "Aon3D": ["Deeptech / Robotics / AR/VR"],
    "Beatdapp": ["Gaming / Media / Entertainment", "Web3 / Crypto"],
    "Botpress": ["Dev Tools / Cloud"],
    "Certn": ["Future of Work", "Cybersecurity"],
    "Chemshift Technologies": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Clutch": ["Transportation / Mobility", "Consumer"],
    "Cybrid": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "Dreamwell AI": ["Gaming / Media / Entertainment"],
    "Edda": ["FinTech / Insurance"],
    "Eli Health": ["Health"],
    "FightCamp": ["Consumer"],
    "Gia": ["Future of Work"],
    "Greeneye Technology": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "HumanFirst": ["Future of Work"],
    "Lancey": ["Future of Work"],
    "Nera": ["Dev Tools / Cloud"],
    "Perceptive Space": ["Deeptech / Robotics / AR/VR", "Data & Analytics"],
    "Poppy": ["Health", "Deeptech / Robotics / AR/VR"],
    "SIX": ["Consumer"],
    "Smart Access": ["Future of Work"],
    "TISC": ["Data & Analytics"],
    "VVEAVE": ["Consumer", "Deeptech / Robotics / AR/VR"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in soup.select('[role="listitem"].wixui-repeater__item'):
        h4 = [clean(h.get_text(" ")) for h in it.select("h4")]
        h4 = [h for h in h4 if h and h != "\u200b"]
        if not h4:
            continue
        name = h4[0]
        if name.lower() in seen:
            continue
        p = it.select_one("p")
        desc = clean(p.get_text(" ")) if p else None
        a = it.select_one('a[data-testid="linkElement"][href^=http]')
        loc = h4[1] if len(h4) > 1 else None
        seen.add(name.lower())
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(a["href"]) if a else None,
            "location": loc,
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
    for k in ("description", "company_url", "location", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
