#!/usr/bin/env python3
"""Concept Ventures portfolio scraper -> concept_companies.json
Source: https://concept.vc/portfolio — Webflow CMS list (Finsweet sort /
filter), server-rendered. Each card (data-portfolio-id = slug) carries a
modal with the description, Founders, Founded and Website, plus an "Exit"
badge (shown only for exited companies). The listing shows logos only, so
the company name is read from each /portfolio/<slug> detail page's <h1>
(which also has a one-line tagline).
Status: visible Exit badge -> acquired; otherwise blank (no active label).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, year_of, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://concept.vc/portfolio"
DETAIL = "https://concept.vc/portfolio/{}"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "concept_companies.json")
PRIMARY = "Concept Ventures"

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Capably": [
        "Future of Work"
    ],
    "Semaloop": [
        "Dev Tools / Cloud"
    ],
    "ArgoX": [
        "FinTech / Insurance"
    ],
    "MindMax": [
        "Consumer"
    ],
    "Architect": [
        "Dev Tools / Cloud"
    ],
    "Archestra": [
        "Dev Tools / Cloud",
        "Cybersecurity"
    ],
    "Fabra": [
        "Deeptech / Robotics / AR/VR",
        "Dev Tools / Cloud"
    ],
    "Arondite": [
        "RegTech/Gov/Legal",
        "Deeptech / Robotics / AR/VR"
    ],
    "Dex": [
        "Future of Work"
    ],
    "Anam": [
        "Dev Tools / Cloud",
        "Gaming / Media / Entertainment"
    ],
    "Jigcar": [
        "Transportation / Mobility",
        "Consumer"
    ],
    "V-Sim": [
        "Deeptech / Robotics / AR/VR",
        "Dev Tools / Cloud"
    ],
    "Digital Iron": [
        "Consumer",
        "Health"
    ],
    "Wrisk": [
        "FinTech / Insurance"
    ],
    "Playgap": [
        "Gaming / Media / Entertainment",
        "Data & Analytics"
    ],
    "Verax AI": [
        "Dev Tools / Cloud",
        "Cybersecurity"
    ],
    "Symbe": [
        "Future of Work"
    ],
    "Harriet": [
        "Future of Work"
    ],
    "Gendo": [
        "Dev Tools / Cloud",
        "PropTech"
    ],
    "Waypoint": [
        "Consumer"
    ],
    "Sohar Health": [
        "Health"
    ],
    "Treefera": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Spectinga": [
        "Consumer"
    ],
    "Ontik": [
        "FinTech / Insurance",
        "Logistics / Supply Chain"
    ],
    "Condense": [
        "Gaming / Media / Entertainment",
        "Deeptech / Robotics / AR/VR"
    ],
    "Cliff.ai": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Emperia": [
        "Consumer",
        "Deeptech / Robotics / AR/VR"
    ],
    "ElevenLabs": [
        "Gaming / Media / Entertainment",
        "Dev Tools / Cloud"
    ],
    "PeopleForce": [
        "Future of Work"
    ],
    "Superlinked": [
        "Dev Tools / Cloud",
        "Data & Analytics"
    ],
    "Track Titan": [
        "Gaming / Media / Entertainment",
        "Data & Analytics"
    ],
    "Landmark Games": [
        "Gaming / Media / Entertainment"
    ],
    "Skiller Whale": [
        "Future of Work",
        "Dev Tools / Cloud"
    ],
    "Captur": [
        "Transportation / Mobility",
        "Deeptech / Robotics / AR/VR"
    ],
    "Playter": [
        "FinTech / Insurance"
    ],
}


def visible(el):
    return el is not None and "w-condition-invisible" not in (el.get("class") or [])


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards = []
    for it in soup.select("div.portfolio-collection-item.w-dyn-item[data-portfolio-id]"):
        slug = it["data-portfolio-id"]
        if slug not in [c[0] for c in cards]:
            cards.append((slug, it))
    if limit:
        cards = cards[:limit]
    pages = fetch_many([DETAIL.format(s) for s, _ in cards])
    out, seen = [], set()
    for slug, it in cards:
        url = DETAIL.format(slug)
        name = tagline = None
        if pages.get(url):
            d = BeautifulSoup(pages[url], "html.parser")
            h1 = d.find("h1")
            name = clean(h1.get_text(" ")) if h1 else None
            t = clean(d.title.get_text(" ")) if d.title else None
            if t and name and t.startswith(name + " | "):
                tagline = clean(t[len(name) + 3:])
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        dd = it.select_one(".modal-text-wrapper > .text-size-regular")
        desc = clean(dd.get_text(" ")) if dd else None
        info, site = {}, None
        for w in it.select(".modal-detail-wrapper"):
            lab = w.select_one(".modal-label")
            if not lab:
                continue
            key = clean(lab.get_text(" ")).lower()
            a = w.select_one("a[href^=http]")
            if key == "website" and a:
                site = a["href"]
            v = w.select_one(".text-size-regular")
            info[key] = clean(v.get_text(" ")) if v else None
        exited = visible(it.select_one(".exit-tag"))
        out.append({
            "company_name": name,
            "description": desc or tagline,
            "tagline": tagline,
            "company_url": clean_url(site),
            "company_profile_url": url,
            "status": "acquired" if exited else None,
            "site_status": "Exit" if exited else None,
            "year_founded": year_of(info.get("founded")),
            "founders": [clean(x) for x in re.split(r",| & | and ", info.get("founders") or "") if clean(x)],
            "everywhere_tags": tags_for(name, " ".join(x for x in (tagline, desc) if x)),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, None)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "year_founded", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
