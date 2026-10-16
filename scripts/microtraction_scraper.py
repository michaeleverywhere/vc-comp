#!/usr/bin/env python3
"""Microtraction portfolio scraper -> microtraction_companies.json
Source: https://www.microtraction.com/portfolio — Webflow/Finsweet list: name,
country, one-line description, sector, founded/partnered years, founding team,
stage, website.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, stage_label
from _d50_common import rec, finish

SOURCE_URL = "https://www.microtraction.com/portfolio"
PRIMARY = "Microtraction"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"], "health tech": ["Health"],
              "crypto": ["Web3 / Crypto"], "ecommerce": ["Consumer"], "foodtech": ["CPG"], "saas": ["Future of Work"],
              "logistics": ["Logistics / Supply Chain"], "edtech": ["Consumer"], "hr": ["Future of Work"],
              "entertainment": ["Gaming / Media / Entertainment"], "gaming": ["Gaming / Media / Entertainment"],
              "creator economy": ["Gaming / Media / Entertainment"], "mobility": ["Transportation / Mobility"],
              "proptech": ["PropTech"], "agritech": ["Climate / Sustainability"], "cleantech": ["Climate / Sustainability"]}


def f(it, sel):
    e = it.select_one(sel)
    return clean(e.get_text(" ", strip=True)) if e else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".w-dyn-item"):
        name = f(it, '[fs-cmsfilter-field="name"]')
        if not name:
            continue
        ms = it.select_one(".c-portfolio-details-milestones")
        mtxt = ms.get_text(" ", strip=True) if ms else ""
        fy = re.search(r"Founded\s+(\d{4})", mtxt)
        py = re.search(r"Partnered\s+(\d{4})", mtxt)
        team = it.select_one(".c-portfolio-details-team p.bold")
        founders = [clean(x) for x in re.split(r",|\n| & | and ", team.get_text("\n")) if clean(x)] if team else []
        a = it.select_one(".c-portfolio-details-explore-wrap a[href^=http]")
        stage = f(it, '[fs-cmsfilter-field="stage"]')
        sector = f(it, '[fs-cmsfilter-field="sector"]')
        out.append(rec(name, f(it, ".c-portfolio-item-description"), a["href"] if a else None, PRIMARY, SOURCE_URL,
                       scraped_at, sectors=[sector] if sector else [], sector_map=SECTOR_MAP, location=f(it, '[fs-cmsfilter-field="countries"]'),
                       founders=founders, stage=stage_label(stage), stage_raw=stage,
                       year_founded=int(fy.group(1)) if fy else None,
                       first_invested_year=int(py.group(1)) if py else None))
    finish(out, "microtraction", ("description", "company_url", "location", "stage", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
