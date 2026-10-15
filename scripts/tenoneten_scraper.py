#!/usr/bin/env python3
"""TenOneTen Ventures portfolio scraper -> tenoneten_companies.json
Source: https://tenoneten.net/portfolio — Webflow CMS list .portfolio-clw-news
(the vertical moving grids are animation duplicates of a smaller subset).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://tenoneten.net/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "tenoneten_companies.json")
PRIMARY = "TenOneTen"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    root = soup.select_one(".portfolio-clw-news") or soup
    for it in root.select(".w-dyn-item"):
        name = None
        for sel in ["p.team-text-block", ".portfolio-title", "h3", "p"]:
            el = it.select_one(sel)
            if el and clean(el.get_text(" ")):
                name = clean(el.get_text(" "))
                break
        if not name or name.lower() in seen or len(name) > 80:
            continue
        # skip category chrome
        if name.lower() in ("all", "active", "acquired", "ipo"):
            continue
        seen.add(name.lower())
        founders = []
        # founder may sit in adjacent headings
        first = clean(it.select_one("h3").get_text(" ")) if it.select_one("h3") and name not in (clean(it.select_one("h3").get_text(" ")) or "") else None
        # description
        desc = None
        for el in it.select("p"):
            t = clean(el.get_text(" "))
            if t and t != name and len(t) > 20:
                desc = t
                break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": None,
            "founders": founders,
            "sectors": [],
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
