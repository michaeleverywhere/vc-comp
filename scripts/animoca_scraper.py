#!/usr/bin/env python3
"""Animoca Brands portfolio scraper -> animoca_companies.json
Source: https://www.animocabrands.com/our-portfolio — Webflow CMS list (paginated):
company/project name, website link, X profile and portfolio category (Gaming,
Infrastructure, DeFi, AI, ...). The site publishes no descriptions.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.animocabrands.com/our-portfolio"
PRIMARY = "Animoca Brands"
SECTOR_MAP = {"gaming": ["Gaming / Media / Entertainment", "Web3 / Crypto"], "defi": ["Web3 / Crypto", "FinTech / Insurance"],
              "infrastructure": ["Web3 / Crypto"], "depin": ["Web3 / Crypto"], "rwa": ["Web3 / Crypto"], "btc": ["Web3 / Crypto"],
              "social": ["Web3 / Crypto", "Consumer"], "culture": ["Web3 / Crypto"], "ai": ["Web3 / Crypto"], "others": ["Web3 / Crypto"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".collection-item"):
            t = it.select_one(".portfolio-text")
            if not t or not clean(t.get_text()):
                continue
            links = [a["href"].strip() for a in it.select(".logo-icons a[href^=http]")]
            site = next((h for h in links if not is_social(h)), None)
            x = next((h for h in links if "x.com/" in h or "twitter.com/" in h), None)
            cats = [clean(c.get_text()) for c in it.select('[fs-list-field="portfolio_category"]') if clean(c.get_text())]
            out.append(rec(t.get_text(" ", strip=True), None, site, PRIMARY, SOURCE_URL, scraped_at,
                           sectors=cats, sector_map=SECTOR_MAP, twitter_url=x))
    finish(out, "animoca", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
