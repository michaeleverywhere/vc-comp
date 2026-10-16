#!/usr/bin/env python3
"""Voyager Ventures portfolio scraper -> voyager_companies.json
Source: https://www.voyagervc.com/portfolio — Webflow/Finsweet cards (paginated ?<hash>_page=N) with name,
short + long description, website, sector, region, first-investment round,
industry, location, year founded.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, stage_label, year_of, webflow_pages
from _d50_common import rec, finish

SOURCE_URL = "https://www.voyagervc.com/portfolio"
PRIMARY = "Voyager Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    infos = []
    for html in webflow_pages(SOURCE_URL):
        infos += BeautifulSoup(html, "html.parser").select(".portfolio-card__info")
    out = []
    for info in infos:
        box = info.parent
        nm = info.select_one(".portfolio-info__name")
        if not nm:
            continue
        data = {}
        for h in info.select(".portfolio-info__data-list-item"):
            k = h.find("div")
            v = h.select_one(".portfolio-info__data-item")
            if k and v:
                data[clean(k.get_text()).rstrip(":").lower()] = clean(v.get_text(" ", strip=True))
        sd = info.select_one(".portfolio-info__short-desc")
        ld = info.select_one(".portfolio-info__long-desc")
        w = info.select_one("a.portfolio-info__website[href]")
        sector = box.select_one('[fs-list-field="sector"]')
        region = box.select_one('[fs-list-field="location"]')
        sectors = [x for x in {clean(sector.get_text()) if sector else None, data.get("industry")} if x]
        fi = data.get("first investment")
        out.append(rec(nm.get_text(" ", strip=True), (ld or sd).get_text(" ", strip=True) if (ld or sd) else None,
                       w["href"] if w else None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors,
                       tagline=sd.get_text(" ", strip=True) if sd else None, location=data.get("location"),
                       region=clean(region.get_text()) if region else None, first_investment_round=fi,
                       stage=stage_label(fi), year_founded=year_of(data.get("year founded"))))
    finish(out, "voyager", ("description", "company_url", "location", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
