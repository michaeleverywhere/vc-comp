#!/usr/bin/env python3
"""Space Capital portfolio scraper -> spacecapital_companies.json
Source: https://www.spacecapital.com/portfolio — Webflow list of
a.c-portfolio-item-link (name, Industry + Tech Layer labels) + detail pages
(Founded in year, HQ, tagline, company overview, Visit Website link).
"""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, fetch_many, label_after, year_of,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.spacecapital.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "spacecapital_companies.json")
PRIMARY = "Space Capital"
SECTOR_TAG_MAP = {k: ["Deeptech / Robotics / AR/VR"] for k in ("satellites", "launch", "stations", "lunar", "transport")}
SECTOR_TAG_MAP.update({"geoint": ["Data & Analytics"], "satcom": [], "applications": [], "distribution": [],
                       "infrastructure": [], "services": []})
TAG_OVERRIDES = {  # judgment pass (no LLM)
    "Solar Foods": ["Climate / Sustainability", "CPG"], "Afference": ["Deeptech / Robotics / AR/VR"],
    "Arbol": ["FinTech / Insurance", "Climate / Sustainability", "Data & Analytics"], "Gradial": ["Gaming / Media / Entertainment", "Future of Work"],
    "Regrow": ["Climate / Sustainability", "Data & Analytics"], "Bliq": ["Transportation / Mobility", "Logistics / Supply Chain"],
    "Cognitive3D": ["Deeptech / Robotics / AR/VR", "Data & Analytics"], "echo3D": ["Deeptech / Robotics / AR/VR", "Dev Tools / Cloud"],
    "dataPlor": ["Data & Analytics"], "ClearRoad": ["Transportation / Mobility", "RegTech/Gov/Legal"],
    "Matidor": ["Data & Analytics"], "Mobius Labs": ["Data & Analytics", "Dev Tools / Cloud"], "aKin": ["Deeptech / Robotics / AR/VR", "Health"],
    "Allevi": ["BioTech", "Deeptech / Robotics / AR/VR"], "Roadio": ["Transportation / Mobility", "Data & Analytics"],
    "Quantum Xchange": ["Cybersecurity", "Deeptech / Robotics / AR/VR"], "Panthalassa": ["Climate / Sustainability", "Deeptech / Robotics / AR/VR"],
}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a.c-portfolio-item-link[href]"):
        p = a.select_one("p.c-text-2")
        name = clean(p.get_text(" ")) if p else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        labels = [clean(sp.get_text()) for sp in a.select(".c-text-softer span") if clean(sp.get_text()) not in (None, ",")]
        out.append({"company_name": name, "detail_url": urljoin(SOURCE_URL, a["href"]),
                    "sectors": [l for l in labels if l]})
    pages = fetch_many([r["detail_url"] for r in out], workers=5, pause=0.15)
    for r in out:
        html = pages.get(r["detail_url"])
        tagline = overview = url = hq = None
        founded = None
        if html:
            ds = BeautifulSoup(html, "html.parser")
            m = ds.select_one("main") or ds.body or ds
            strings = [clean(x) for x in m.stripped_strings if clean(x)]
            founded = year_of(label_after(strings, "Founded in"))
            try:
                i = strings.index("Founded in")
                hq = strings[i + 2] if len(strings) > i + 2 and not year_of(strings[i + 2]) else None
                tagline = next((s for s in strings[i + 3:i + 6] if len(s) > 40), None)
            except ValueError:
                pass
            overview = label_after(strings, "COMPANY OVERVIEW")
            go = next((x for x in m.select("a[href^=http]") if "visit website" in x.get_text(" ").lower()), None)
            url = clean_url(go["href"]) if go else None
        r.update({
            "description": overview or tagline,
            "tagline": tagline,
            "company_url": url,
            "location": hq,
            "year_founded": founded,
            "profile_url": r.pop("detail_url"),
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        mapped = [t for lab in r["sectors"] for t in SECTOR_TAG_MAP.get(lab.lower(), [])]
        kw = tags_for(r["company_name"], tagline or overview)  # text only: layer words like
        tags = []                                              # "Infrastructure" are not sectors
        for t in mapped + kw:
            if t not in tags:
                tags.append(t)
        r["everywhere_tags"] = tags[:3]
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "tagline", "company_url", "location", "year_founded", "everywhere_tags"))


if __name__ == "__main__":
    main()
