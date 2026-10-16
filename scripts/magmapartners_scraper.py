#!/usr/bin/env python3
"""Magma Partners portfolio scraper -> magmapartners_companies.json
Source: https://magmapartners.com/companies — Webflow list: name, one-liner,
investment year, stage, industry, female-founded flag; plus each company page:
website ("visit website"), founding team, locations.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish, page_strings

SOURCE_URL = "https://magmapartners.com/companies"
PRIMARY = "Magma Partners"
STAGES = {"seed", "pre-seed", "series a", "series b"}
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"], "lending": ["FinTech / Insurance"],
              "proptech": ["PropTech"], "logistics": ["Logistics / Supply Chain"], "health": ["Health"],
              "cybersecurity": ["Cybersecurity"], "web3": ["Web3 / Crypto"], "media": ["Gaming / Media / Entertainment"],
              "dtc": ["Consumer"], "consumer": ["Consumer"], "foodtech": ["CPG"], "agtech": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    items = []
    for it in soup.select(".mc-companies__list > .w-dyn-item"):
        a = it.select_one("a.mc-company__item-content[href]")
        h = it.select_one("h4")
        if not a or not h:
            continue
        p = a.select_one("p")
        tags = [clean(t.get_text(" ", strip=True)) for t in it.select(".mc-filter__tag")
                if "w-condition-invisible" not in (t.get("class") or []) and clean(t.get_text(" ", strip=True))]
        items.append((clean(h.get_text(" ", strip=True)), clean(p.get_text(" ", strip=True)) if p else None,
                      urljoin(SOURCE_URL, a["href"]), tags))
    pages = fetch_many([i[2] for i in items], workers=6, pause=0.1)
    out = []
    for name, desc, link, tags in items:
        year = next((year_of(t) for t in tags if year_of(t) and len(t) == 4), None)
        stage = next((t for t in tags if t.lower() in STAGES), None)
        ff = any(t.lower() == "female founded" for t in tags)
        secs = [t for t in tags if not (year_of(t) and len(t) == 4) and t.lower() not in STAGES and t.lower() != "female founded"]
        site, team, locs = None, [], []
        if pages.get(link):
            st, s = page_strings(pages[link])
            for a in s.select("a[href^=http]"):
                if a.get_text(" ", strip=True).lower() == "visit website" and not is_social(a["href"]):
                    site = a["href"]; break
            low = [x.lower() for x in st]
            if "founding team" in low:
                i = low.index("founding team") + 1
                while i < len(st) and low[i] not in ("locations",):
                    team.append(st[i]); i += 1
            if "locations" in low:
                i = low.index("locations") + 1
                while i < len(st) and len(st[i]) < 40 and low[i] not in ("industry", "stage", "year", "back to companies", "no items found."):
                    locs.append(st[i]); i += 1
                locs = locs[:1]
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=secs, sector_map=SECTOR_MAP,
                       first_invested_year=year, stage=stage, female_founded=ff or None, founders=team,
                       location=", ".join(locs) or None, detail_url=link))
    finish(out, "magmapartners", ("description", "company_url", "first_invested_year", "stage", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
