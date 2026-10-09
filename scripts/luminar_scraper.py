#!/usr/bin/env python3
"""Luminar Ventures portfolio scraper -> luminar_companies.json
Source: https://www.luminarventures.com/portfolio — Webflow CMS list
(Finsweet filters), server-rendered: name, headline, Sector, Focus
(B2B / B2C), Luminar stage label (Early / Growth — a fund-stage bucket, not
a funding round, so `stage` stays blank and the raw label is kept in
`luminar_stage`), founders and a status tag (Active / Exit). Each
/portfolio/<slug> detail page adds the company website and the long
description (text after the Status row).
Status: Active -> active; Exit -> acquired (raw kept in site_status).
"""
import json, os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, clean_url, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.luminarventures.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "luminar_companies.json")
PRIMARY = "Luminar Ventures"
STATUS = {"active": "active", "exit": "acquired"}
SECTOR_TAG_MAP = {
    "open finance": ["FinTech / Insurance"], "green transition": ["Climate / Sustainability"],
    "digital health": ["Health"], "creative consumer": ["Consumer"],
}

# Hand-reviewed tag fixes (judgment pass, no LLM). Applied after keyword tagging.
TAG_OVERRIDES = {
    "Albacross": [
        "Data & Analytics"
    ],
    "Aviant": [
        "Deeptech / Robotics / AR/VR",
        "Logistics / Supply Chain",
        "Health"
    ],
    "Berget AI": [
        "Dev Tools / Cloud"
    ],
    "Carla": [
        "Transportation / Mobility",
        "Consumer",
        "Climate / Sustainability"
    ],
    "CodeScene": [
        "Dev Tools / Cloud"
    ],
    "Corsmed": [
        "Health"
    ],
    "Deckmatch": [
        "FinTech / Insurance",
        "Data & Analytics"
    ],
    "Fika Jobs": [
        "Future of Work"
    ],
    "FirstQFM": [
        "Deeptech / Robotics / AR/VR"
    ],
    "Greenely": [
        "Climate / Sustainability",
        "Consumer"
    ],
    "Health Integrator": [
        "Health"
    ],
    "Heja": [
        "Consumer"
    ],
    "Hypertype": [
        "Future of Work"
    ],
    "Insurello": [
        "FinTech / Insurance"
    ],
    "Insurely": [
        "FinTech / Insurance"
    ],
    "Intuicell": [
        "Deeptech / Robotics / AR/VR"
    ],
    "IPercept": [
        "Data & Analytics",
        "Deeptech / Robotics / AR/VR"
    ],
    "Ivy": [
        "Dev Tools / Cloud"
    ],
    "Lightbringer": [
        "RegTech/Gov/Legal"
    ],
    "Mindler": [
        "Health"
    ],
    "Motorica": [
        "Gaming / Media / Entertainment",
        "Deeptech / Robotics / AR/VR"
    ],
    "Mynt": [
        "FinTech / Insurance"
    ],
    "Normative": [
        "Climate / Sustainability",
        "Data & Analytics"
    ],
    "Omocom": [
        "FinTech / Insurance"
    ],
    "OpenPayments": [
        "FinTech / Insurance"
    ],
    "Opper": [
        "Dev Tools / Cloud"
    ],
    "Pet Buddy Group": [
        "CPG",
        "Consumer"
    ],
    "Photoncycle": [
        "Climate / Sustainability"
    ],
    "Pley": [
        "Gaming / Media / Entertainment"
    ],
    "ReCarber": [
        "Climate / Sustainability"
    ],
    "RockyRoad": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "RUN": [
        "FinTech / Insurance",
        "Gaming / Media / Entertainment"
    ],
    "Starmony": [
        "Gaming / Media / Entertainment",
        "Consumer"
    ],
    "Turbotic": [
        "Future of Work",
        "Data & Analytics"
    ],
    "Vården": [
        "Health"
    ],
    "Vibrant": [
        "FinTech / Insurance"
    ],
    "xNomad": [
        "Consumer",
        "PropTech"
    ],
    "Yazen": [
        "Health"
    ],
    "Muninn": [
        "Cybersecurity"
    ],
}


def detail(html):
    if not html:
        return None, None
    s = BeautifulSoup(html, "html.parser")
    for x in s(["script", "style", "noscript", "svg"]):
        x.decompose()
    site = None
    strings = [clean(t) for t in s.stripped_strings]
    strings = [t for t in strings if t]
    for i, t in enumerate(strings):
        if t == "Website" and i + 1 < len(strings):
            dom = strings[i + 1].lower().strip("/ ")
            for a in s.select("a[href^=http]"):
                if dom and dom.split("/")[0] in a["href"].lower():
                    site = a["href"]
                    break
            break
    desc = None
    if "Status" in strings:
        i = strings.index("Status")
        tail = strings[i + 2:]
        stop = next((j for j, t in enumerate(tail) if t in ("Why we invested", "Deal Lead", "Related news")), len(tail))
        desc = clean(" ".join(tail[:stop])) or None
    return site, desc


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards, seen = [], set()
    for it in soup.select("div.company-card__item.w-dyn-item"):
        lab = it.select_one(":scope > .label")
        name = clean(lab.get_text(" ")) if lab else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        cards.append((name, it))
    if limit:
        cards = cards[:limit]
    links = {name: urljoin(SOURCE_URL, it.select_one("a.company-card__link")["href"]) for name, it in cards if it.select_one("a.company-card__link[href]")}
    pages = fetch_many(list(links.values()))
    out = []
    for name, it in cards:
        f = lambda k: [clean(x.get_text(" ")) for x in it.select(f'[fs-cmsfilter-field="{k}"]') if clean(x.get_text(" "))]
        sectors, focus, stage = f("sector"), f("focus"), (f("stage") or [None])[0]
        h3 = it.select_one(".company-card__title")
        tagline = clean(h3.get_text(" ")) if h3 else None
        founders = [clean(x.get_text(" ")) for x in it.select(".company-card__founders .post__tag") if clean(x.get_text(" ")) and "w-condition-invisible" not in x.get("class", [])]
        st = it.select_one(".post__tag.right-corner")
        raw = clean(st.get_text(" ")) if st else None
        site, desc = detail(pages.get(links.get(name)))
        out.append({
            "company_name": name,
            "description": desc or tagline,
            "tagline": tagline,
            "company_url": clean_url(site),
            "company_profile_url": links.get(name),
            "status": STATUS.get((raw or "").lower()),
            "site_status": raw,
            "luminar_stage": stage,
            "focus": focus,
            "founders": founders,
            "sectors": sectors,
            "everywhere_tags": tags_for(name, " ".join(x for x in (tagline, desc) if x), sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "sectors", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
