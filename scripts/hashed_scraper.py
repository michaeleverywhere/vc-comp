#!/usr/bin/env python3
"""Hashed portfolio scraper -> hashed_companies.json
Source: https://www.hashed.com/portfolio/ — Gatsby page grouped by category
(section h1); each item has name, description, website, location, founders.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.hashed.com/portfolio/"
PRIMARY = "Hashed"
SECTOR_MAP = {"blockchain platforms": ["Web3 / Crypto"], "financial infrastructure": ["Web3 / Crypto", "FinTech / Insurance"],
              "picks & shovels": ["Web3 / Crypto"], "applications": ["Web3 / Crypto"], "defi": ["Web3 / Crypto", "FinTech / Insurance"],
              "gaming": ["Gaming / Media / Entertainment"], "web3 gaming": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
              "infrastructure": ["Web3 / Crypto"], "nft": ["Web3 / Crypto"], "fintech": ["FinTech / Insurance"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for grp in soup.select("section[class*=portfolio-group]"):
        h = grp.select_one("h1")
        cat = clean(h.get_text(" ", strip=True)) if h else None
        for li in grp.select("li[class*=portfolio-list--item]"):
            nm = li.select_one("[class*=company-name]")
            if not nm:
                continue
            meta = {}
            for g in li.select("[class*=metadata--group]"):
                t = g.select_one("[class*=metadata-title]")
                if not t:
                    continue
                k = clean(t.get_text()).lower()
                a = g.select_one("a[href]")
                v = a["href"] if (a and k == "website") else clean(g.get_text(" ", strip=True)[len(t.get_text()):])
                meta[k] = v
            d = li.select_one("[class*=description]")
            founders = [clean(x) for x in (meta.get("founder") or meta.get("founders") or "").split(",") if clean(x)]
            out.append(rec(nm.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None, meta.get("website"),
                           PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [], sector_map=SECTOR_MAP,
                           location=meta.get("location"), founders=founders))
    finish(out, "hashed", ("description", "company_url", "location", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
