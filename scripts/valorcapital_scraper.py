#!/usr/bin/env python3
"""Valor Capital Group portfolio scraper -> valorcapital_companies.json
Source: https://valorcapitalgroup.com/companies/ — SSR cards
(.companies-list__item.js-company-item) with data-* attrs for name, description,
website, location, and an Exit badge.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url, tags_for, apply_tag_overrides
from _d20_common import write_out

SOURCE_URL = "https://valorcapitalgroup.com/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "valorcapital_companies.json")
PRIMARY = "Valor Capital Group"
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".companies-list__item.js-company-item"):
        name = clean(it.get("data-title"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(it.get("data-text"))
        website = clean_url(it.get("data-link"))
        location = clean(it.get("data-location"))
        status = "acquired" if it.select_one(".companies-list__item-tag") and "exit" in it.get_text(" ").lower() else None
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "location": location,
            "status": status,
            "sectors": [],
            "everywhere_tags": tags_for(name, desc),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
    apply_tag_overrides(out, TAG_OVERRIDES)
    out.sort(key=lambda r: r["company_name"].lower())
    write_out(out, OUT, ("description", "company_url", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
