#!/usr/bin/env python3
"""Variant portfolio scraper -> variant_companies.json
Source: https://variant.fund/portfolio/ — WordPress page; each
<a class="portfolio-item"> links to the company website, carries the name,
a category slug (data-portfolio-categories: infra / apps / new-markets) and a
meta line "<Round>, <Year>" = the round Variant entered at and the year
(e.g. "Series B, 2026"). stage only when that label is a real funding round
("Strategic" is not, kept in entry_label). The site publishes no descriptions;
those are filled from company websites via scripts/fill_descriptions_web.py and
carried forward on re-runs. No location/status published.
"""
import os, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, year_of, stage_label,
                             carry_forward_descriptions, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://variant.fund/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "variant_companies.json")
PRIMARY = "Variant"
CAT_LABELS = {"infra": "Infrastructure", "apps": "Apps", "new-markets": "New Markets"}
SECTOR_TAG_MAP = {}  # Variant is a crypto fund; Web3 / Crypto added below.
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select("a.portfolio-item"):
        n = it.select_one(".portfolio-item__name")
        name = clean(n.get_text(" ")) if n else clean(it.get("data-sort-name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        d = it.select_one(".portfolio-item__description")
        desc = clean(d.get_text(" ")) if d else None
        meta = it.select_one(".portfolio-item__meta")
        meta = clean(meta.get_text(" ")) if meta else None
        label = clean(meta.rsplit(",", 1)[0]) if meta and "," in meta else meta
        cats = [CAT_LABELS.get(c, c) for c in (it.get("data-portfolio-categories") or "").split() if c]
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean_url(it.get("href")),
            "sectors": cats,
            "entry_label": label,
            "stage": stage_label(label),
            "first_invested": year_of(meta) or year_of(it.get("data-sort-year")),
            "everywhere_tags": [],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    carry_forward_descriptions(out, OUT)
    for r in out:
        tags = tags_for(r["company_name"], r.get("description"), None, SECTOR_TAG_MAP)
        r["everywhere_tags"] = (["Web3 / Crypto"] + [t for t in tags if t != "Web3 / Crypto"])[:4]
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "stage", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
