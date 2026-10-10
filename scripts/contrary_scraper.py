#!/usr/bin/env python3
"""Contrary portfolio scraper -> contrary_companies.json
Source: https://contrary.com/companies — Next.js (Prismic) server-rendered
list. Each row: company name (`p.text-h3-mobile`), one-paragraph description
(`p.text-sm-mobile`) and icon links (Twitter / LinkedIn / Website — the
`img[alt=Website]` link is the company site). No stage, location, dates or
status are published.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, clean_url, prune_substring_tags, apply_tag_overrides

SOURCE_URL = "https://contrary.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "contrary_companies.json")
PRIMARY = "Contrary"
SECTOR_TAG_MAP = {}
# Hand-reviewed tag fixes (judgment pass, no LLM).
TAG_OVERRIDES = {
    "Ando": [
        "Future of Work"
    ],
    "Base": [
        "Climate / Sustainability"
    ],
    "Brightland": [
        "CPG",
        "Consumer"
    ],
    "FSH Technologies": [
        "RegTech/Gov/Legal"
    ],
    "Fractional": [
        "PropTech",
        "FinTech / Insurance"
    ],
    "Hallow": [
        "Consumer",
        "Health"
    ],
    "Lightyear": [
        "Dev Tools / Cloud"
    ],
    "Nomic": [
        "Data & Analytics",
        "Dev Tools / Cloud"
    ],
    "Pave": [
        "Future of Work",
        "Data & Analytics"
    ],
    "Recurrency": [
        "Logistics / Supply Chain"
    ],
    "Tava Health": [
        "Health"
    ],
    "Vesto": [
        "FinTech / Insurance"
    ],
    "Warp": [
        "Dev Tools / Cloud"
    ],
    "Parfait": [
        "Consumer",
        "CPG"
    ],
    "Moment": [
        "FinTech / Insurance",
        "Dev Tools / Cloud"
    ],
    "Patch": [
        "Climate / Sustainability",
        "Dev Tools / Cloud"
    ],
    "Power": [
        "Health"
    ],
    "Voltra": [
        "Climate / Sustainability"
    ],
    "Orchard Robotics": [
        "Deeptech / Robotics / AR/VR",
        "Climate / Sustainability"
    ],
    "Anduril": [
        "Deeptech / Robotics / AR/VR",
        "RegTech/Gov/Legal"
    ],
    "Modern Intelligence": [
        "Deeptech / Robotics / AR/VR",
        "RegTech/Gov/Legal"
    ],
    "Endeavor": [
        "Future of Work",
        "Logistics / Supply Chain"
    ],
    "Leland": [
        "Future of Work",
        "Consumer"
    ],
    "Sora Schools": [
        "Consumer"
    ],
    "Doss": [
        "Data & Analytics",
        "Logistics / Supply Chain"
    ],
    "Armada": [
        "Dev Tools / Cloud"
    ],
    "Zepto": [
        "Consumer",
        "Logistics / Supply Chain"
    ]
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in soup.select("p.text-h3-mobile"):
        name = clean(p.get_text(" "))
        row = p
        while row is not None and not row.select_one("p.text-sm-mobile"):
            row = row.parent
        if not name or row is None or name.lower() in seen:
            continue
        seen.add(name.lower())
        dp = row.select_one("p.text-sm-mobile")
        desc = clean(dp.get_text(" ")) if dp else None
        img = row.select_one('a[href^=http] img[alt="Website"]')
        site = clean_url(img.find_parent("a")["href"]) if img else None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "everywhere_tags": tags_for(name, desc, [], SECTOR_TAG_MAP),
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
    for k in ("description", "company_url", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
