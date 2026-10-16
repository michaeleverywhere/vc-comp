#!/usr/bin/env python3
"""Arrington Capital portfolio scraper -> arrington_companies.json
Source: https://www.arringtoncapital.com/portfolio/ — WordPress grid of portfolio
blocks (name + category tags such as L1, L2, DeFi, NFT) and matching modals
(description, website, X profile), joined by data-modal / modal-N index.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.arringtoncapital.com/portfolio/"
PRIMARY = "Arrington Capital"
SECTOR_MAP = {"defi": ["Web3 / Crypto", "FinTech / Insurance"], "nft": ["Web3 / Crypto"], "gaming": ["Gaming / Media / Entertainment", "Web3 / Crypto"],
              "l1": ["Web3 / Crypto"], "l2": ["Web3 / Crypto"], "infrastructure": ["Web3 / Crypto"], "ethereum": ["Web3 / Crypto"],
              "bitcoin": ["Web3 / Crypto"], "solana": ["Web3 / Crypto"], "depin": ["Web3 / Crypto"], "cefi": ["Web3 / Crypto", "FinTech / Insurance"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch_response(SOURCE_URL).content, "html.parser")
    modals = {}
    for m in soup.select("div.modal[data-name]"):
        idx = next((c[6:] for c in m.get("class") or [] if c.startswith("modal-") and c[6:].isdigit()), None)
        if idx is not None:
            modals[idx] = m
    out = []
    for b in soup.select("div.portfolio-block[data-name]"):
        name = clean(b.get("data-name")) or (clean(b.find("h4").get_text()) if b.find("h4") else None)
        if not name:
            continue
        tags = [clean(t.get_text()) for t in b.select(".post-tag") if clean(t.get_text())]
        m = modals.get(b.get("data-modal"))
        desc = site = x = None
        if m is not None:
            d = m.select_one(".portfolio-description")
            desc = clean(d.get_text(" ", strip=True)) if d else None
            w = m.select_one("a.portfolio-website[href^=http]")
            site = w["href"] if w else None
            t = m.select_one(".link.twitter a[href]")
            x = t["href"] if t else None
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=tags, sector_map=SECTOR_MAP, twitter_url=x))
    finish(out, "arrington", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
