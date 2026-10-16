#!/usr/bin/env python3
"""Fenbushi Capital portfolio scraper -> fenbushi_companies.json
Source: https://fenbushi.vc/projects/ — server-rendered tiles
(`.portfolio-tile__wrapper`): project name, website link and category list
(data-regions JSON attribute, e.g. ["DeFi"]). No descriptions are published.
"""
import os, sys, json
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://fenbushi.vc/projects/"
PRIMARY = "Fenbushi Capital"
SECTOR_MAP = {"defi": ["Web3 / Crypto"], "infra": ["Web3 / Crypto"], "cefi": ["Web3 / Crypto"],
              "gamefi/nft": ["Web3 / Crypto", "Gaming / Media / Entertainment"], "security/audit": ["Web3 / Crypto", "Cybersecurity"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for w in soup.select(".portfolio-tile__wrapper"):
        nm = w.select_one(".portfolio-tile__meta__name")
        if not nm:
            continue
        try:
            cats = [clean(c) for c in json.loads(w.get("data-regions") or "[]") if clean(c)]
        except ValueError:
            cats = []
        a = w.select_one("a.portfolio-tile[href]")
        href = a["href"] if a else ""
        out.append(rec(nm.get_text(" ", strip=True), None, href if href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=cats, sector_map=SECTOR_MAP))
    finish(out, "fenbushi", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
