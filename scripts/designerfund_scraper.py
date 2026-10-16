#!/usr/bin/env python3
"""Designer Fund portfolio scraper -> designerfund_companies.json
Source: https://designerfund.com/ — Framer portfolio cards (data-framer-name
Card/Category/Name/Short Description for featured companies, plus
'Company Box' name+category tiles for the full list) linking to each company site.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://designerfund.com/"
PRIMARY = "Designer Fund"
SECTOR_MAP = {"financial infrastructure": ["FinTech / Insurance"], "preventative health": ["Health"],
              "collaborative tools": ["Future of Work"], "developer tools": ["Dev Tools / Cloud"],
              "healthcare": ["Health"], "healthcare infra": ["Health"], "mental health": ["Health"],
              "health testing": ["Health"], "femtech": ["Health"], "design tools": ["Dev Tools / Cloud"],
              "design tool": ["Dev Tools / Cloud"], "3d design tool": ["Dev Tools / Cloud"],
              "climate tech": ["Climate / Sustainability"], "home electrification": ["Climate / Sustainability"],
              "renewable energy": ["Climate / Sustainability"], "climate financing": ["Climate / Sustainability", "FinTech / Insurance"],
              "construction tech": ["PropTech"], "edtech": ["Consumer"], "education": ["Consumer"],
              "fintech": ["FinTech / Insurance"], "personal finance": ["FinTech / Insurance"], "neobank": ["FinTech / Insurance"],
              "financial wellness": ["FinTech / Insurance"], "financial services": ["FinTech / Insurance"],
              "accounting software": ["FinTech / Insurance"], "anti money laundering": ["RegTech/Gov/Legal", "FinTech / Insurance"],
              "legal tech": ["RegTech/Gov/Legal"], "crypto marketplace": ["Web3 / Crypto"], "crypto wallet": ["Web3 / Crypto"],
              "payroll & benefits": ["Future of Work"], "benefits platform": ["Future of Work"], "hiring platform": ["Future of Work"],
              "enterprise messaging": ["Future of Work"], "remote collaboration": ["Future of Work"],
              "productivity tools": ["Future of Work"], "email productivity": ["Future of Work"], "product management": ["Future of Work"],
              "ai app builder": ["Dev Tools / Cloud"], "ai app development": ["Dev Tools / Cloud"], "no-code page builder": ["Dev Tools / Cloud"],
              "data collaboration": ["Data & Analytics"], "ecommerce": ["Consumer"], "commerce": ["Consumer"],
              "travel": ["Transportation / Mobility", "Consumer"], "event ticketing": ["Gaming / Media / Entertainment"],
              "online events": ["Gaming / Media / Entertainment"], "ai storytelling": ["Gaming / Media / Entertainment"],
              "parenting tools": ["Consumer"], "hospitality": ["Consumer"], "maps": ["Data & Analytics"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    cards = soup.select('a[data-framer-name="Card"][href^=http]') + \
        soup.select('a[data-framer-name^="Company Box"][href^=http]')
    for card in cards:
        g = lambda k: (lambda e: clean(e.get_text(" ", strip=True)) if e else None)(card.select_one(f'[data-framer-name="{k}"]'))
        name = g("Name") or g("Company Name")
        if not name:
            continue
        cat = g("Category")
        out.append(rec(name, g("Short Description"), card["href"], PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[cat] if cat else [], sector_map=SECTOR_MAP))
    finish(out, "designerfund")


if __name__ == "__main__":
    main()
