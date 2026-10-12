#!/usr/bin/env python3
"""Intel Capital portfolio scraper -> intelcapital_companies.json
Source: https://www.intelcapital.com/portfolio/ — SSR HTML; each .company card
carries name on the spotlight <a alt="..."> (fallback .company-title), a blurb
in the link text, sector-ish CSS classes (cloud/ai/edge/...), and region classes
(north-america/emea/...). No funding round published. Status not published.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.intelcapital.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "intelcapital_companies.json")
PRIMARY = "Intel Capital"
SECTOR_TAG_MAP = {
    "ai": ["Data & Analytics"], "cloud": ["Dev Tools / Cloud"], "edge": ["Deeptech / Robotics / AR/VR"],
    "security": ["Cybersecurity"], "silicon": ["Deeptech / Robotics / AR/VR"],
    "devices": ["Consumer"], "network": ["Dev Tools / Cloud"],
    "frontier": ["Deeptech / Robotics / AR/VR"], "software": ["Dev Tools / Cloud"],
}
REGION_SKIP = {"fadein", "company", "current", "prior", "north-america", "emea", "asia-pacific",
               "latin-america", "israel", "china", "india", "japan", "korea", "taiwan", "other",
               "western-europe"}
TAG_OVERRIDES = {
    "Fabric8Labs": ["Deeptech / Robotics / AR/VR"], "AMFG": ["Deeptech / Robotics / AR/VR", "Dev Tools / Cloud"],
    "Biofourmis": ["Health"], "caresyntax": ["Health"], "Deep Sentinel": ["Cybersecurity"],
    "Delair": ["Deeptech / Robotics / AR/VR"], "FieldAI": ["Deeptech / Robotics / AR/VR", "Data & Analytics"],
    "Figure AI": ["Deeptech / Robotics / AR/VR"], "Formant": ["Deeptech / Robotics / AR/VR", "Dev Tools / Cloud"],
    "Healx": ["BioTech", "Health"], "Inrix": ["Transportation / Mobility", "Data & Analytics"],
    "MatrixSpace": ["Deeptech / Robotics / AR/VR"], "MDI Health": ["Health"], "OliverIQ": ["Data & Analytics"],
    "OXMIQ Labs": ["Deeptech / Robotics / AR/VR"], "Q-Factor": ["Deeptech / Robotics / AR/VR"],
    "R3": ["FinTech / Insurance", "Web3 / Crypto"], "Retrace": ["Health"], "SaVia": ["Health"],
    "SiPhox": ["Health", "Deeptech / Robotics / AR/VR"], "Skylo": ["Deeptech / Robotics / AR/VR"],
    "TriEye": ["Deeptech / Robotics / AR/VR"], "VeriSIM Life": ["BioTech"],
    "ZeroEyes": ["Cybersecurity", "Deeptech / Robotics / AR/VR"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for c in soup.select(".company"):
        a = c.select_one("a[alt]") or c.select_one('a[href*="/story/"]')
        title = c.select_one(".company-title")
        name = clean(a.get("alt") if a and a.get("alt") else None) or (clean(title.get_text(" ")) if title else None)
        if not name:
            href = (a.get("href") if a else "") or ""
            m = re.search(r"/story/([^/]+)/?", href)
            if m:
                name = clean(m.group(1).replace("-", " ").title())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = None
        if a:
            txt = clean(a.get_text(" "))
            if txt:
                desc = clean(re.sub(r"\s*Founder Story.*$", "", txt, flags=re.I))
        classes = [cl for cl in (c.get("class") or []) if cl.lower() not in REGION_SKIP]
        sectors = classes
        loc = None
        for cl in (c.get("class") or []):
            cll = cl.lower()
            if cll in ("north-america", "emea", "asia-pacific", "latin-america", "israel", "china", "india", "japan", "korea", "taiwan"):
                loc = cl.replace("-", " ").title()
                break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": None,  # firm site links to Intel story pages, not company sites
            "sectors": sectors,
            "location": loc,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "location", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
