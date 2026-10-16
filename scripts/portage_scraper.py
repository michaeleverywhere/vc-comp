#!/usr/bin/env python3
"""Portage (Sagard) portfolio scraper -> portage_companies.json
Source: https://portageinvest.com/portfolio — Webflow CMS list (paginated):
name, description, sector / region / fund tags; detail page for website.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, fetch_many, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://portageinvest.com/portfolio"
PRIMARY = "Portage"
REGIONS = {"Europe", "Latin America", "Middle East", "North America", "Oceania", "Other"}
FUNDS = {"Portage Capital Solutions", "Portage Ventures", "Secondaries"}
SECTOR_MAP = {"insurance": ["FinTech / Insurance"], "payments": ["FinTech / Insurance"],
              "smb & consumer finance": ["FinTech / Insurance"], "wealth & asset management": ["FinTech / Insurance"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    items = []
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".portfolio_list > .w-dyn-item"):
            t = it.select_one('[portfolio="title"]')
            if not t:
                continue
            d = it.select_one(".portfolio_card_right")
            a = it.select_one("a.link-full[href]") or it.select_one("a[href^='/clients/']")
            tags = [clean(x.get_text(strip=True)) for x in it.select("[data-tag-slug]")]
            items.append((clean(t.get_text(" ", strip=True)), clean(d.get_text(" ", strip=True)) if d else None,
                          urljoin(SOURCE_URL, a["href"]) if a else None, tags))
    pages = fetch_many([i[2] for i in items if i[2]], workers=6, pause=0.1)
    out = []
    for name, desc, link, tags in items:
        site = None
        if link and pages.get(link):
            s = BeautifulSoup(pages[link], "html.parser")
            for a in s.select("a[href^=http]"):
                if "visit website" in (a.get("aria-label") or a.get_text(" ", strip=True)).lower() and not is_social(a["href"]):
                    site = a["href"]; break
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[t for t in tags if t not in REGIONS and t not in FUNDS], sector_map=SECTOR_MAP,
                       region=", ".join(t for t in tags if t in REGIONS) or None,
                       fund=", ".join(t for t in tags if t in FUNDS) or None, detail_url=link))
    finish(out, "portage", ("description", "company_url", "region", "everywhere_tags"))


if __name__ == "__main__":
    main()
