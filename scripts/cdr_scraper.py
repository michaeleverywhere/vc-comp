#!/usr/bin/env python3
"""Clayton, Dubilier & Rice portfolio scraper -> cdr_companies.json
Source: https://www.cdr.com/portfolio — server-rendered card grid (sector tag,
name, region, investment year, detail link); each detail page adds the
description and Company Website (dl/dt/dd fields). The page lists CD&R's
current portfolio only.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.cdr.com/portfolio"
PRIMARY = "Clayton, Dubilier & Rice"
SECTOR_MAP = {"healthcare": ["Health"], "consumer, retail & services": ["Consumer"],
              "financial services": ["FinTech / Insurance"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    for c in soup.select("div.card"):
        a = c.select_one("a.card-link[href]")
        if not a:
            continue
        sectors = [clean(x.get_text(" ", strip=True)) for x in c.select("a[href*='sectors=']")]
        reg = c.select_one(".f-body-1 p")
        t = c.select_one("time")
        cards.append((a["href"], a.get_text(" ", strip=True), sectors,
                      clean(reg.get_text(" ", strip=True)) if reg else None, t.get("datetime") if t else None))
    pages = fetch_many([c[0] for c in cards])
    out = []
    for url, name, sectors, region, yr in cards:
        d = BeautifulSoup(pages.get(url) or "", "html.parser")
        w = d.select_one(".wysiwyg")
        desc = " ".join(p.get_text(" ", strip=True) for p in w.find_all("p")) if w else None
        site = None
        for dt in d.select("dt"):
            if clean(dt.get_text()) == "Company Website":
                a = dt.find_next("dd").find("a", href=True) if dt.find_next("dd") else None
                if a and a["href"].startswith("http") and not is_social(a["href"]):
                    site = a["href"]
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP,
                       region=region, first_invested_year=year_of(yr or ""), portfolio_status="Current",
                       status="active", detail_url=url))
    finish(out, "cdr", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
