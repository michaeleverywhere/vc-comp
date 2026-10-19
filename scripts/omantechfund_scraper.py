#!/usr/bin/env python3
"""Oman Technology Fund (OTF Scale / Oman Future Fund) portfolio scraper ->
omantechfund_companies.json
Source: https://www.otf.om/ — portfolio cards (client-rendered, read via headless Chrome):
company name, OTF sector label and one-line description. The cards link to on-site
profiles only (no company websites)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_dom import dom

SOURCE_URL = "https://www.otf.om/"
PRIMARY = "Oman Technology Fund"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "e-commerce": ["Consumer"], "tourism": ["Consumer"],
              "cybersecurity": ["Cybersecurity"], "mobility": ["Transportation / Mobility"],
              "logistics": ["Logistics / Supply Chain"], "proptech": ["PropTech"], "edtech": ["Future of Work"],
              "healthtech": ["Health"], "agritech": ["Climate / Sustainability"], "foodtech": ["CPG"],
              "gaming": ["Gaming / Media / Entertainment"], "media": ["Gaming / Media / Entertainment"],
              "energy": ["Climate / Sustainability"], "cleantech": ["Climate / Sustainability"],
              "hr tech": ["Future of Work"], "edutech": ["Future of Work"], "consumer services": ["Consumer"], "iot": ["Deeptech / Robotics / AR/VR"], "climatetech": ["Climate / Sustainability"], "enterprise software": [], "deeptech / ai": ["Deeptech / Robotics / AR/VR"], "legaltech": ["RegTech/Gov/Legal"], "ai": [], "saas": []}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(dom(SOURCE_URL, 15000, min_len=20000), "html.parser")
    out = []
    for a in s.select('a[href^="#startup/"]'):
        parts = [clean(x.get_text(" ", strip=True)) for x in a.select(".sc-interp")]
        parts = [p for p in parts if p and p.lower() != "view profile"]
        if not parts:
            continue
        lab = clean(re.sub(r"(?i)^view profile:\s*", "", a.get("aria-label") or ""))
        if lab and parts[0] != lab and lab in parts:
            parts = parts[parts.index(lab):]  # drop the monogram shown when a card has no logo
        name = lab or parts[0]
        sector = parts[1] if len(parts) >= 2 else None
        desc = parts[2] if len(parts) >= 3 else None
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sector] if sector else [],
                       sector_map=SECTOR_MAP, profile_url=SOURCE_URL + a["href"]))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} OTF companies")
    finish(out, "omantechfund", ("description", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
