#!/usr/bin/env python3
"""Western Technology Investment (WTI) portfolio scraper -> wti_companies.json
Source: https://www.westerntech.com/companies — Webflow CMS company list (paginated via
the list's ?9d6f5d1c_page=N "next" links, 100 per page): company name, website, initial
WTI investment year, description, and hidden filter values for region, sector(s) and
status (Acquired / Public / Private / Inactive). WTI is a venture lender (venture debt)
backing venture-funded startups."""
import os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.westerntech.com/companies"
PRIMARY = "Western Technology Investment"
STATUS = {"acquired": "acquired", "public": "public", "private": "active", "inactive": "closed"}
REGIONS = {"africa", "asia", "canada", "europe", "latin america", "middle east", "oceania", "united states"}
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "insurance": ["FinTech / Insurance"],
              "health": ["Health"], "consumer": ["Consumer"], "climate": ["Climate / Sustainability"],
              "environment": ["Climate / Sustainability"], "hardware": ["Deeptech / Robotics / AR/VR"],
              "aerospace": ["Deeptech / Robotics / AR/VR"], "real estate": ["PropTech"],
              "transportation": ["Transportation / Mobility"], "media & gaming": ["Gaming / Media / Entertainment"],
              "workforce": ["Future of Work"], "food": ["CPG"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, url, seen = [], SOURCE_URL, set()
    while url and url not in seen and len(seen) < 40:
        seen.add(url)
        s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
        lst = s.select_one(".filters-collection-list")
        if not lst:
            break
        for it in lst.select(":scope > .w-dyn-item"):
            card = it.select_one(".company-card")
            if not card:
                continue
            a = card.select_one("a.company-name")
            nm = card.select_one(".company-name-box .company-name")
            name = clean(nm.get_text(" ", strip=True)) if nm else None
            if not name:
                continue
            href = (a.get("href") or "") if a and "w-condition-invisible" not in (a.get("class") or []) else ""
            yr = card.select_one(".initial-investment-label")
            yr = clean(yr.get_text(" ", strip=True)) if yr else None
            d = card.select_one(".company-desc")
            desc = clean(d.get_text(" ", strip=True)) if d else None
            hidden = [clean(x.get_text(" ", strip=True)) for x in card.select(".hidden-filters > div")]
            hidden = [h for h in hidden if h]
            status = next((STATUS[h.lower()] for h in hidden if h.lower() in STATUS), None)
            region = next((h for h in hidden if h.lower() in REGIONS), None)
            sectors = [h for h in hidden if h.lower() not in STATUS and h.lower() not in REGIONS]
            out.append(rec(name, desc, href if href.startswith("http") else None, PRIMARY, SOURCE_URL,
                           scraped_at, sectors=sectors, sector_map=SECTOR_MAP, location=region,
                           first_invested=yr if yr and re.fullmatch(r"(19|20)\d\d", yr) else None,
                           status=status))
        nxt = s.select_one("a.w-pagination-next[href]")
        url = urljoin(url, nxt["href"]) if nxt else None
    finish(out, "wti", ("description", "company_url", "location", "first_invested", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
