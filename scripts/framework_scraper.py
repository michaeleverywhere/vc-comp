#!/usr/bin/env python3
"""Framework Ventures portfolio scraper -> framework_companies.json
Source: https://framework.ventures/portfolio — .portfolio_list_item with name
and optional external website. Crypto/web3 fund; descriptions not on index.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import (fetch, clean, tags_for, clean_url, is_social,
                             prune_substring_tags, apply_tag_overrides, carry_forward_descriptions)
from _d20_common import write_out

SOURCE_URL = "https://framework.ventures/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "framework_companies.json")
PRIMARY = "Framework Ventures"
SECTOR_TAG_MAP = {}
TAG_OVERRIDES = {}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for it in soup.select(".portfolio_list_item"):
        title = it.select_one(".portfolio_list_title") or it.select_one("h2, h3, h4")
        name = clean(title.get_text(" ")) if title else None
        if not name:
            name = clean(it.get_text(" "))
        if not name or name.lower() in seen or name.lower() in ("jobs", "portfolio"):
            continue
        seen.add(name.lower())
        url = None
        for a in it.select("a[href^=http]"):
            u = a["href"]
            if "framework.ventures" in u or is_social(u):
                continue
            url = clean_url(u)
            if url:
                break
        out.append({
            "company_name": name,
            "description": None,
            "company_url": url,
            "sectors": ["Web3"],
            "everywhere_tags": tags_for(name, None, ["Web3"], {"web3": ["Web3 / Crypto"]}) or ["Web3 / Crypto"],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    filled = carry_forward_descriptions(out, OUT)
    for r in out:
        r["everywhere_tags"] = tags_for(r["company_name"], r.get("description"), r.get("sectors"), {"web3": ["Web3 / Crypto"]}) or ["Web3 / Crypto"]
    prune_substring_tags(out, {"web3": ["Web3 / Crypto"]})
    apply_tag_overrides(out, TAG_OVERRIDES)
    write_out(out, OUT, ("description", "company_url", "everywhere_tags"))
    if filled:
        print(f"  carried_forward_descriptions: {len(filled)}")


if __name__ == "__main__":
    main()
