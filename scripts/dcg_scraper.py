#!/usr/bin/env python3
"""Digital Currency Group portfolio scraper -> dcg_companies.json
Source: https://dcg.co/portfolio — Webflow CMS list (.folio__item): name, city,
description, first-investment date, website, category, region, status.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://dcg.co/portfolio"
PRIMARY = "Digital Currency Group"
SECTOR_MAP = {"payments": ["FinTech / Insurance"], "web3 infrastructure": ["Web3 / Crypto"],
              "exchanges": ["Web3 / Crypto", "FinTech / Insurance"], "identity, compliance & security": ["Cybersecurity"],
              "defi": ["Web3 / Crypto", "FinTech / Insurance"], "metaverse, nfts & gaming": ["Web3 / Crypto", "Gaming / Media / Entertainment"],
              "wallets & custody": ["Web3 / Crypto"], "trading tools & platforms": ["FinTech / Insurance"],
              "data & analytics": ["Data & Analytics"], "analytics": ["Data & Analytics"], "deai": ["Web3 / Crypto"],
              "fintech": ["FinTech / Insurance"], "blockchains - l1s & l2s": ["Web3 / Crypto"], "privacy": ["Cybersecurity"],
              "stablecoins & rwa's": ["Web3 / Crypto", "FinTech / Insurance"], "stablecoins": ["Web3 / Crypto"],
              "banks": ["FinTech / Insurance"], "depin": ["Web3 / Crypto"]}


def t(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".folio__item.w-dyn-item"):
        name = t(it.select_one(".folio__name")) or t(it.select_one(".folio__name-list"))
        site = it.select_one("a.item__sitelink")
        cat = t(it.select_one(".folio__category"))
        status = t(it.select_one(".folio__status"))
        fi = t(it.select_one(".folio__year"))
        out.append(rec(name, t(it.select_one(".portfolio__item-desc")), site["href"] if site else None, PRIMARY,
                       SOURCE_URL, scraped_at, sectors=[cat] if cat else [], sector_map=SECTOR_MAP,
                       location=t(it.select_one(".folio__city-country")), region=t(it.select_one(".folio__region")),
                       first_investment_date=fi, first_invested_year=year_of(fi),
                       status=(status.lower() if status else "active")))
    finish(out, "dcg", ("description", "company_url", "location", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
