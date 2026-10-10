#!/usr/bin/env python3
"""Root Ventures portfolio scraper -> rootventures_companies.json
Source: https://root.vc/ (portfolio section, /#tldr) — static page whose
JSON-LD @graph lists every portfolio company as an Organization with
funder = Root Ventures (name, one-line description, website). The visible
"Portfolio" list mirrors it. The site publishes no stages, dates, locations
or exit statuses.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://root.vc/#tldr"
PAGE = "https://root.vc/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "rootventures_companies.json")
PRIMARY = "Root Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {  # hand-reviewed against Root's one-liners (no LLM)
    "Superconductive": ["Data & Analytics", "Dev Tools / Cloud"],
    "nTopology": ["Deeptech / Robotics / AR/VR"],
    "Tortuga AgTech": ["Deeptech / Robotics / AR/VR", "Climate / Sustainability"],
    "Instrumental": ["Data & Analytics", "Deeptech / Robotics / AR/VR"],
    "Stellar Pizza": ["Deeptech / Robotics / AR/VR", "CPG"],
    "Versatile": ["PropTech", "Data & Analytics"],
    "Wildtype Foods": ["CPG", "BioTech"],
    "Nordsense": ["Climate / Sustainability", "Logistics / Supply Chain"],
    "TruckLabs": ["Transportation / Mobility", "Logistics / Supply Chain"],
    "Sensable": ["Data & Analytics", "Deeptech / Robotics / AR/VR"],
    "Crux": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
    "Mashgin": ["Consumer", "Deeptech / Robotics / AR/VR"],
    "Creator": ["Deeptech / Robotics / AR/VR", "CPG"],
    "ApolloShield": ["Cybersecurity", "RegTech/Gov/Legal"],
    "Skycatch": ["Data & Analytics", "Deeptech / Robotics / AR/VR"],
    "Shaper": ["Deeptech / Robotics / AR/VR"],
    "Cape": ["Dev Tools / Cloud"],
    "Righthook": ["Transportation / Mobility", "Dev Tools / Cloud"],
    "SixWheel": ["Transportation / Mobility", "Climate / Sustainability"],
    "Zed": ["Dev Tools / Cloud"],
    "Kayhan": ["Deeptech / Robotics / AR/VR"],
    "AllSpice": ["Dev Tools / Cloud", "Deeptech / Robotics / AR/VR"],
    "Quilter": ["Deeptech / Robotics / AR/VR"],
    "Adept": ["Deeptech / Robotics / AR/VR"],
    "Aperture Data": ["Data & Analytics", "Dev Tools / Cloud"],
    "Fudge": ["Dev Tools / Cloud"],
    "Kodra": ["Data & Analytics", "Dev Tools / Cloud"],
    "Topologic": ["Deeptech / Robotics / AR/VR"],
    "Ruby Robotics": ["Health", "Deeptech / Robotics / AR/VR"],
    "Instance": ["BioTech"],
    "CADY Solutions": ["Deeptech / Robotics / AR/VR"],
    "Determinate Systems": ["Dev Tools / Cloud"],
    "Gen Alpha": ["Deeptech / Robotics / AR/VR"],
    "Hunch": ["Data & Analytics"],
    "Illoca": ["PropTech"],
    "Subtrace": ["Dev Tools / Cloud"],
    "Loopwork": ["Dev Tools / Cloud"],
    "Feather": ["Deeptech / Robotics / AR/VR", "Dev Tools / Cloud"],
    "Vibe Robotics": ["Deeptech / Robotics / AR/VR", "Dev Tools / Cloud"],
    "Loombotic": ["Deeptech / Robotics / AR/VR"],
    "Ground Control Dev": ["PropTech"],
    "PhyAgents": ["Deeptech / Robotics / AR/VR"],
    "Lithos Computer": ["Dev Tools / Cloud"],
    "Breakpoint AI": ["Dev Tools / Cloud", "Data & Analytics"],
    "Daily": ["Dev Tools / Cloud"],
    "Esper": ["Dev Tools / Cloud"],
    "Particle": ["Dev Tools / Cloud", "Deeptech / Robotics / AR/VR"],
    "Nautilus Labs": ["Logistics / Supply Chain", "Climate / Sustainability"],
    "Seismic": ["Deeptech / Robotics / AR/VR", "Health"],
    "Seam": ["Dev Tools / Cloud", "PropTech"],
    "Radical": ["Cybersecurity", "Deeptech / Robotics / AR/VR"],
    "Latent Technology": ["Gaming / Media / Entertainment"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(PAGE), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for sc in soup.select('script[type="application/ld+json"]'):
        try:
            data = json.loads(sc.string or "")
        except ValueError:
            continue
        graph = data.get("@graph", [data]) if isinstance(data, dict) else data
        for o in graph:
            if not isinstance(o, dict) or o.get("@type") != "Organization" or not o.get("funder"):
                continue
            name = clean(o.get("name"))
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            desc = clean(o.get("description"))
            out.append({
                "company_name": name,
                "description": desc,
                "company_url": clean_url(o.get("url")),
                "everywhere_tags": tags_for(name, desc or "", [], SECTOR_TAG_MAP),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
    if limit:
        out = out[:limit]
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
