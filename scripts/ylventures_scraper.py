#!/usr/bin/env python3
"""YL Ventures portfolio scraper -> ylventures_companies.json
Source: https://www.ylventures.com/portfolio/ — WordPress page, fully
server-rendered. Each company has a grid trigger card (logo image alt = name,
field label) and a modal carousel slide carrying Founders, Founded, Field,
HQ, an intro paragraph, website link and, for exits, Company name +
"Acquired by". No stage or investment year is published.
Status: slides flagged data-company-status="1" with an "Acquired by" value ->
acquired (acquirer kept); the others carry no status label, so status stays
blank (YL does not label them active).
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, year_of, apply_tag_overrides, prune_substring_tags

SOURCE_URL = "https://www.ylventures.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "ylventures_companies.json")
PRIMARY = "YL Ventures"

# Hand-reviewed tags (judgment pass, no LLM). YL is a cybersecurity-only fund.
TAG_OVERRIDES = {
    "Novee": ["Cybersecurity"],
    "Native": ["Cybersecurity", "Dev Tools / Cloud"],
    "Opti": ["Cybersecurity"],
    "Hush": ["Cybersecurity", "Dev Tools / Cloud"],
    "MIND": ["Cybersecurity", "Data & Analytics"],
    "Miggo": ["Cybersecurity", "Dev Tools / Cloud"],
    "Minimus": ["Cybersecurity", "Dev Tools / Cloud"],
    "Autonomous Security": ["Cybersecurity"],
    "Valence Security": ["Cybersecurity"],
    "Grip Security": ["Cybersecurity"],
    "Cycode": ["Cybersecurity", "Dev Tools / Cloud"],
    "Orca Security": ["Cybersecurity", "Dev Tools / Cloud"],
    "Hunters": ["Cybersecurity", "Data & Analytics"],
    "Ride Vision": ["Transportation / Mobility", "Deeptech / Robotics / AR/VR"],
    "Aim Security": ["Cybersecurity"],
    "Satori": ["Cybersecurity", "Data & Analytics"],
    "Vulcan Cyber": ["Cybersecurity"],
    "Eureka Security": ["Cybersecurity", "Dev Tools / Cloud"],
    "Spera Security": ["Cybersecurity"],
    "Enso Security": ["Cybersecurity", "Dev Tools / Cloud"],
    "Medigate": ["Cybersecurity", "Health"],
    "build.security": ["Cybersecurity", "Dev Tools / Cloud"],
    "Axonius": ["Cybersecurity"],
    "Twistlock": ["Cybersecurity", "Dev Tools / Cloud"],
    "Hexadite": ["Cybersecurity"],
    "FireLayers": ["Cybersecurity", "Dev Tools / Cloud"],
    "BlazeMeter": ["Dev Tools / Cloud"],
    "Clicktale": ["Data & Analytics"],
    "Upstream Commerce": ["Data & Analytics", "Consumer"],
    "Seculert": ["Cybersecurity"],
    "AcceloWeb": ["Dev Tools / Cloud"],
    "Opus Security": ["Cybersecurity"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    alt = {}
    for t in soup.select(".modal-portfolio-trigger[data-company]"):
        img = t.select_one("img.card__img-mobile") or t.select_one("img[alt]")
        if img and clean(img.get("alt")):
            alt[t["data-company"].lstrip("#")] = clean(img["alt"])
    out, seen = [], set()
    for sl in soup.select("div.carousel-item.company-block[data-company]"):
        key = sl["data-company"].lstrip("#")
        info = {}
        for it in sl.select(".information-item[data-item]"):
            p = it.select_one("p")
            info[it["data-item"]] = clean(p.get_text(" ")) if p else None
        name = info.get("company-name") or alt.get(key)
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        intro = sl.select_one("p.into-info")
        desc = clean(intro.get_text(" ")) if intro else None
        web = sl.select_one("li.website a[href]")
        acq = info.get("acquired-by")
        field = info.get("field")
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": clean_url(web["href"]) if web else None,
            "status": "acquired" if acq else None,
            "acquirer": acq,
            "location": info.get("hq"),
            "year_founded": year_of(info.get("founded")),
            "founders": [clean(x) for x in (info.get("founders") or "").split(",") if clean(x)],
            "sectors": [field] if field else [],
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        tags = tags_for(name, " ".join(x for x in (desc, field) if x))
        if "Cybersecurity" not in tags:
            tags = ["Cybersecurity"] + tags
        rec["everywhere_tags"] = tags[:4]
        out.append(rec)
        if limit and len(out) >= limit:
            break
    prune_substring_tags(out, None)
    for r in out:  # security fund: the core tag survives pruning
        if "Cybersecurity" not in r["everywhere_tags"]:
            r["everywhere_tags"] = (["Cybersecurity"] + r["everywhere_tags"])[:4]
    apply_tag_overrides(out, TAG_OVERRIDES)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "location", "year_founded", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
