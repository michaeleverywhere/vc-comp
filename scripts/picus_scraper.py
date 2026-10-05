#!/usr/bin/env python3
"""Picus Capital portfolio scraper -> picus_companies.json
Source: https://www.picuscap.com/portfolio/ — WordPress; all companies are
server-rendered as hexagon tiles (li.hex): name (p#demo1), one-paragraph
description (p#demo2), outbound link (company site; one tile links Wikipedia,
kept as website_link) and a UNICORN badge (li.hex.is-unicorn). The site does not
publish sector, stage, location, invest year or exit status.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://www.picuscap.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "picus_companies.json")
PRIMARY = "Picus Capital"
NON_SITE = ("wikipedia.org", "linkedin.com", "crunchbase.com", "twitter.com", "x.com/")

# Hand-assigned tags (reviewer judgment from the firm-site description; no LLM)
# for companies the keyword classifier leaves untagged. Applied only when empty.
TAG_OVERRIDES = {
    "Billie": [
        "FinTech / Insurance"
    ],
    "Limehome": [
        "PropTech",
        "Consumer"
    ],
    "Landbase": [
        "Future of Work"
    ],
    "Rex": [
        "Health"
    ],
    "Miscusi": [
        "Consumer"
    ],
    "Vega": [
        "FinTech / Insurance"
    ],
    "Blitzy": [
        "Dev Tools / Cloud"
    ],
    "Niva": [
        "RegTech/Gov/Legal"
    ],
    "Joblift": [
        "Future of Work"
    ],
    "Lightbase": [
        "Dev Tools / Cloud"
    ],
    "Gotrade": [
        "FinTech / Insurance"
    ],
    "D2X": [
        "Web3 / Crypto",
        "FinTech / Insurance"
    ],
    "Inkle": [
        "FinTech / Insurance",
        "RegTech/Gov/Legal"
    ],
    "Prima": [
        "Logistics / Supply Chain"
    ],
    "Genus AI": [
        "Data & Analytics"
    ],
    "Conduit Tech": [
        "PropTech",
        "Climate / Sustainability"
    ],
    "Sento": [
        "Future of Work"
    ],
    "DualEntry": [
        "FinTech / Insurance"
    ],
    "Clau": [
        "PropTech"
    ],
    "XO Market": [
        "FinTech / Insurance"
    ]
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for li in soup.select("li.hex"):
        n = li.select_one("#demo1")
        name = clean(n.get_text()) if n else None
        if not name or name.lower() in seen or re.match(r"^\W*and more\W*$", name, re.I):
            continue  # trailing "... and more." filler tile is not a company
        seen.add(name.lower())
        d = li.select_one("#demo2")
        desc = clean(d.get_text(" ")) if d else None
        a = li.select_one("a.portfolio-link-icon[href]")
        link = clean(a["href"]) if a else None
        site = link if link and not any(x in link for x in NON_SITE) else None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "website_link": link if link and not site else None,
            "unicorn": "is-unicorn" in (li.get("class") or []),
            "status": None,
            "stage": None,
            "location": None,
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    for rec in out:
        if not rec["everywhere_tags"] and rec["company_name"] in TAG_OVERRIDES:
            rec["everywhere_tags"] = TAG_OVERRIDES[rec["company_name"]]
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "unicorn", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
