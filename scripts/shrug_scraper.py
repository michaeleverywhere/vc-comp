#!/usr/bin/env python3
"""Shrug Capital portfolio scraper -> shrug_companies.json
Source: https://www.shrug.vc/portfolio — Webflow CMS .w-dyn-item
(name, description, optional website link).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides, webflow_pages)
from _d20_common import write_out

SOURCE_URL = "https://www.shrug.vc/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "shrug_companies.json")
PRIMARY = "Shrug Capital"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".w-dyn-item"):
            name_el = it.select_one(".portfolio-company-name")
            name = clean(name_el.get_text(" ")) if name_el else None
            if not name or name.lower() in seen:
                continue
            seen.add(name.lower())
            desc_el = it.select_one(".portfolio-company-description")
            desc = clean(desc_el.get_text(" ")) if desc_el else None
            if desc and desc.lower() in ("x", "-"):
                desc = None
            url = None
            for a in it.select("a[href^=http]"):
                if "shrug.vc" in a["href"] or is_social(a["href"]):
                    continue
                url = clean_url(a["href"])
                if url:
                    break
            out.append({
                "company_name": name,
                "description": desc,
                "company_url": url,
                "sectors": [],
                "everywhere_tags": tags_for(name, desc),
                "primary_investor": PRIMARY,
                "source_url": SOURCE_URL,
                "scraped_at": scraped_at,
            })
    prune_substring_tags(out)
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
