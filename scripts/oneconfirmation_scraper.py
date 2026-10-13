#!/usr/bin/env python3
"""1confirmation portfolio scraper -> oneconfirmation_companies.json
Source: https://www.1confirmation.com/portfolio — Squarespace .gallery-project
(name, description with Initial Investment date + Website).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides)
from _d20_common import write_out

SOURCE_URL = "https://www.1confirmation.com/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "oneconfirmation_companies.json")
PRIMARY = "1confirmation"
SECTOR_TAG_MAP = {"crypto": ["Web3 / Crypto"], "web3": ["Web3 / Crypto"]}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".gallery-project"):
        title = it.select_one(".project-title")
        name = clean(title.get_text(" ")) if title else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        meta = clean(it.select_one(".project-description").get_text(" ")) if it.select_one(".project-description") else None
        first = None
        url = None
        desc = None
        if meta:
            m = re.search(r"Initial Investment\s*([A-Za-z]+\s+\d{4})", meta)
            if m:
                first = clean(m.group(1))
            m = re.search(r"Website\s*(https?://\S+)", meta)
            if m:
                url = clean_url(m.group(1).rstrip(".,;"))
            # leftover prose before Initial Investment
            prose = re.split(r"Initial Investment", meta, maxsplit=1)[0]
            desc = clean(prose) if prose and len(clean(prose) or "") > 20 else None
        if not url:
            for a in it.select("a[href^=http]"):
                if "1confirmation.com" in a["href"] or is_social(a["href"]):
                    continue
                url = clean_url(a["href"])
                if url:
                    break
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": url,
            "first_invested": first,
            "sectors": ["Web3"],
            "everywhere_tags": tags_for(name, desc, ["Web3"], {"web3": ["Web3 / Crypto"]}) or ["Web3 / Crypto"],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    prune_substring_tags(out, {"web3": ["Web3 / Crypto"]})
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
