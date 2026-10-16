#!/usr/bin/env python3
"""Aisling Capital portfolio scraper -> aisling_companies.json
Source: https://www.aislingcapital.com/portfolio — server-rendered company list
(`li.company`) whose detail panel gives name (h3), ticker, summary and labelled
fields: Year Invested, Fund, Sector, Company Status, Investment Status
(current/historic), Location, Website.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.aislingcapital.com/portfolio"
PRIMARY = "Aisling Capital"
SECTOR_MAP = {"biopharma": ["BioTech"], "medical device": ["Health"], "consumer": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for li in soup.select("li.company"):
        info = li.select_one(".company-details-info")
        if not info or not info.find("h3"):
            continue
        f, site = {}, None
        for row in info.select("ul li"):
            if row.find("h4"):
                k = clean(row.find("h4").get_text()).lower()
                f[k] = clean(row.find("span").get_text(" ", strip=True)) if row.find("span") else None
                a = row.find("a", href=True)
                if k == "website" and a and a["href"].startswith("http") and not is_social(a["href"]):
                    site = a["href"]
        tk = info.select_one(".company-ticker")
        sm = info.select_one(".company-summary")
        inv = (f.get("investment status") or "").lower()
        out.append(rec(info.find("h3").get_text(" ", strip=True), sm.get_text(" ", strip=True) if sm else None, site,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[f["sector"]] if f.get("sector") else [],
                       sector_map=SECTOR_MAP, first_invested_year=year_of(f.get("year invested") or ""),
                       fund=f.get("fund"), company_status=f.get("company status"),
                       ticker=clean(tk.get_text(" ", strip=True)) if tk else None, hq_location=f.get("location"),
                       portfolio_status=f.get("investment status"),
                       status={"current": "active", "historic": "exited"}.get(inv)))
    finish(out, "aisling", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
