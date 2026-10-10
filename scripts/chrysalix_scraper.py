#!/usr/bin/env python3
"""Chrysalix Venture Capital portfolio scraper -> chrysalix_companies.json
Source: https://www.chrysalix.com/portfolio — Framer static page. Each card
(`data-framer-name="Variant N"`) holds: fund (RoboValley Fund / Chrysalix
Energy Fund), status (Active / Exited), name (h3), description, sector label,
LinkedIn + website links. Cards repeat across tab variants -> deduped by name.
status: Active -> active, Exited -> acquired (site's own word kept in
site_status). No locations, rounds or investment dates are published.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, is_social, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://www.chrysalix.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "chrysalix_companies.json")
PRIMARY = "Chrysalix Venture Capital"
SECTOR_TAG_MAP = {
    "forestry decarbonization": ["Climate / Sustainability"], "metals recycling": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "mining ai": ["Deeptech / Robotics / AR/VR"], "mining": ["Deeptech / Robotics / AR/VR"], "industrial ai": ["Deeptech / Robotics / AR/VR"],
    "industrial iot": ["Deeptech / Robotics / AR/VR"], "energy": ["Climate / Sustainability"], "waste water": ["Climate / Sustainability"],
    "advanced materials": ["Deeptech / Robotics / AR/VR"], "metals": ["Deeptech / Robotics / AR/VR"],
}
TAG_OVERRIDES = {
    "Svante": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "General Fusion": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Enbala": ["Climate / Sustainability", "Dev Tools / Cloud"],
    "Liquid Light": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Brammo Motorsports": ["Transportation / Mobility", "Climate / Sustainability"],
    "Minehub Technologies": ["Logistics / Supply Chain", "Data & Analytics"],
    "everox": ["Climate / Sustainability", "PropTech"],
    "GaN Systems": ["Deeptech / Robotics / AR/VR", "Climate / Sustainability"],
    "Liminal Insights": ["Transportation / Mobility", "Data & Analytics", "Climate / Sustainability"],
    "Helmee Imaging": ["Deeptech / Robotics / AR/VR", "Transportation / Mobility"],
    "Q5D Technologies": ["Deeptech / Robotics / AR/VR"],
    "Luffy AI": ["Deeptech / Robotics / AR/VR"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for h in soup.select("h3"):
        card = h
        while card is not None and not (card.name == "div" and (card.get("data-framer-name") or "").startswith("Variant")):
            card = card.parent
        name = clean(h.get_text(" "))
        if card is None or not name or name.lower() in seen:
            continue
        ps = [clean(p.get_text(" ")) for p in card.select("p")]
        ps = [p for p in ps if p]
        if len(ps) < 3:
            continue
        seen.add(name.lower())
        fund, state = ps[0], ps[1]
        desc = ps[2] if len(ps) > 2 else None
        sector = ps[3] if len(ps) > 3 else None
        site = next((a["href"] for a in card.select("a[href^=http]") if not is_social(a["href"])), None)
        st = (state or "").lower()
        sectors = [sector] if sector else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(site) if site else None,
            "fund": fund,
            "sectors": sectors,
            "site_status": state,
            "status": "acquired" if st == "exited" else ("active" if st == "active" else None),
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
    for k in ("description", "company_url", "status", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
