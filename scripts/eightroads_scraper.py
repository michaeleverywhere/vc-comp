#!/usr/bin/env python3
"""Eight Roads portfolio scraper -> eightroads_companies.json
Source: https://www.eightroads.com/en/companies — the page's own JSON feed
(/api/companies, same data the Angular page renders): name, description,
website, sectors, investmentStartDate/EndDate, exited flag; team filter gives
the investing region.
"""
import json, os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.eightroads.com/en/companies"
API = "https://www.eightroads.com/api/companies?language=en&limit=100&page={page}{extra}"
PRIMARY = "Eight Roads"
TEAMS = {"china": "China", "europe-israel": "Europe & Israel", "india": "India", "japan": "Japan"}
SECTOR_MAP = {"consumer": ["Consumer"], "consumer health": ["Health", "Consumer"], "fintech": ["FinTech / Insurance"],
              "healthcare it": ["Health"], "healthcare services": ["Health"], "med tech": ["Health"],
              "pharma & therapeutics": ["BioTech", "Health"]}


def pages(extra=""):
    page, items = 1, []
    while page:
        d = json.loads(fetch(API.format(page=page, extra=extra)))
        items += d.get("items") or []
        page = page + 1 if (d.get("_pagination") or {}).get("next") else None
    return items


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    team_of = {}
    for slug, label in TEAMS.items():
        for it in pages(f"&team={slug}"):
            team_of.setdefault(it["name"], []).append(label)
    out = []
    for it in pages():
        start, end = it.get("investmentStartDate"), it.get("investmentEndDate")
        out.append(rec(it.get("name"), it.get("description"), it.get("website"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[s.get("label") for s in it.get("sectors") or []], sector_map=SECTOR_MAP,
                       first_invested_year=year_of(start), investment_start=start, investment_end=end,
                       region=", ".join(team_of.get(it.get("name"), [])) or None,
                       status="exited" if it.get("exited") else "active"))
    finish(out, "eightroads", ("description", "company_url", "first_invested_year", "region", "everywhere_tags"))


if __name__ == "__main__":
    main()
