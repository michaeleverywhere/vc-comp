#!/usr/bin/env python3
"""Collaborative Fund portfolio scraper -> collaborativefund_companies.json
Source: https://collabfund.com/portfolio/ — static HTML. Two blocks: a
featured "portfolio-sectors" grid (name + Collab's sector pill: AI, Consumer,
Money, Health, Energy) and the full A-Z "portfolio-companies" list (name +
company website link where published). The site publishes no descriptions,
stages, dates or statuses; descriptions are back-filled separately from each
company's own website (scripts/fill_descriptions_web.py), never invented.
"""
import json, os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

SOURCE_URL = "https://collabfund.com/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "collaborativefund_companies.json")
PRIMARY = "Collaborative Fund"
SECTOR_TAG_MAP = {
    "money": ["FinTech / Insurance"], "health": ["Health"], "energy": ["Climate / Sustainability"],
    "consumer": ["Consumer"],
}


def items(block):
    out = []
    for g in block.select(".grid-item") if block else []:
        h = g.select_one("h3")
        name = clean(h.get_text(" ")) if h else None
        if not name:
            continue
        a = g.select_one("a.title-block[href]")
        pill = g.select_one(".sector-label--full")
        out.append({"name": name, "url": a["href"].strip() if a else None,
                    "sector": clean(pill.get_text()) if pill else None})
    return out


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    featured = {}
    for r in items(soup.select_one(".portfolio-sectors")):
        featured.setdefault(r["name"].lower(), []).append(r["sector"])
    prev = None
    try:
        with open(OUT, encoding="utf-8") as fh:
            prev = {x["company_name"].lower(): x for x in json.load(fh)}
    except (OSError, ValueError):
        prev = {}
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for r in items(soup.select_one(".portfolio-companies")):
        key = r["name"].lower()
        if key in seen:
            continue
        seen.add(key)
        sectors = [s for s in featured.get(key, []) if s]
        old = prev.get(key) or {}
        desc = old.get("description")  # keep a previously back-filled company-site blurb
        out.append({
            "company_name": r["name"],
            "description": desc,
            "company_url": r["url"],
            "status": None,
            "sectors": sectors,
            "everywhere_tags": old.get("everywhere_tags") or tags_for(r["name"], desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
