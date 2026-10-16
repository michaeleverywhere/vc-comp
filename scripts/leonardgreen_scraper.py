#!/usr/bin/env python3
"""Leonard Green & Partners portfolio scraper -> leonardgreen_companies.json
Source: https://www.leonardgreen.com/portfolio/ — server-rendered portfolio grid;
each `.work-info .custom-content` block carries company name (h2), HQ (h3),
website link, description (h4) and Sector / Deal Type / Status lines (h5).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.leonardgreen.com/portfolio/"
PRIMARY = "Leonard Green & Partners"
SECTOR_MAP = {"healthcare": ["Health"], "consumer services": ["Consumer"], "consumer products/retail": ["Consumer"],
              "consumer products / retail": ["Consumer"], "financial services": ["FinTech / Insurance"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for c in soup.select(".work-info .custom-content"):
        h2 = c.find("h2")
        if not h2:
            continue
        fields = {}
        for h5 in c.find_all("h5"):
            k, _, v = h5.get_text(" ", strip=True).partition(":")
            fields[k.strip().lower()] = clean(v)
        a = next((a["href"] for a in c.select("a[href^=http]") if not is_social(a["href"])), None)
        status = fields.get("status")
        out.append(rec(h2.get_text(" ", strip=True), c.find("h4") and c.find("h4").get_text(" ", strip=True), a,
                       PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[s for s in (fields.get("sector") or "").split(",") if s.strip()], sector_map=SECTOR_MAP,
                       hq_location=c.find("h3") and c.find("h3").get_text(" ", strip=True),
                       deal_type=fields.get("deal type"), portfolio_status=status,
                       status={"current": "active", "past": "realized"}.get((status or "").lower())))
    finish(out, "leonardgreen", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
