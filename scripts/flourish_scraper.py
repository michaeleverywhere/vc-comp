#!/usr/bin/env python3
"""Flourish Ventures portfolio scraper -> flourish_companies.json
Source: WP REST https://flourishventures.com/wp-json/wp/v2/portfolio — title,
excerpt (description), class_list carries investment-themes-*, region-*, and
funding-series-* (mapped to STAGE only for clear round labels).
"""
import html as htmlmod
import os, re, sys, time
import requests
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (HEADERS, TIMEOUT, clean, tags_for, stage_label,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://flourishventures.com/portfolio/"
API = "https://flourishventures.com/wp-json/wp/v2/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "flourish_companies.json")
PRIMARY = "Flourish Ventures"
SECTOR_TAG_MAP = {
    "infrastructure": ["FinTech / Insurance", "Dev Tools / Cloud"],
    "frontier": ["FinTech / Insurance"],
    "embedded-finance": ["FinTech / Insurance"],
    "embedded finance": ["FinTech / Insurance"],
    "crypto": ["Web3 / Crypto", "FinTech / Insurance"],
    "open-finance": ["FinTech / Insurance"],
    "open finance": ["FinTech / Insurance"],
}
TAG_OVERRIDES = {}


def fetch_all():
    out, page = [], 1
    while True:
        r = requests.get(API, params={"per_page": 100, "page": page, "_fields": "id,title,excerpt,class_list,link"},
                         headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        batch = r.json()
        if not batch:
            break
        out.extend(batch)
        total = int(r.headers.get("X-WP-TotalPages") or 1)
        if page >= total:
            break
        page += 1
        time.sleep(0.2)
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for p in fetch_all():
        name = clean(htmlmod.unescape(p.get("title", {}).get("rendered") or ""))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        excerpt = BeautifulSoup(p.get("excerpt", {}).get("rendered") or "", "html.parser").get_text(" ", strip=True)
        desc = clean(excerpt)
        classes = p.get("class_list") or []
        themes = [c.replace("investment-themes-", "").replace("-", " ") for c in classes if c.startswith("investment-themes-")]
        regions = [c.replace("region-", "").replace("-", " ").title() for c in classes if c.startswith("region-")]
        series_raw = [c.replace("funding-series-", "") for c in classes if c.startswith("funding-series-")]
        stage = None
        for s in series_raw:
            # a/b/c -> Series A; seed -> Seed
            if re.fullmatch(r"[a-h]", s, re.I):
                stage = stage_label("Series " + s.upper())
            else:
                stage = stage_label(s.replace("-", " "))
            if stage:
                break
        loc = regions[0] if regions else None
        out.append({
            "company_name": name,
            "description": desc,
            "sectors": themes,
            "location": loc,
            "stage": stage,
            "everywhere_tags": tags_for(name, desc, themes, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, SECTOR_TAG_MAP)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "stage", "location", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
