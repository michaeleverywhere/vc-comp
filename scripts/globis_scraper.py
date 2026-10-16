#!/usr/bin/env python3
"""Globis Capital Partners portfolio scraper -> globis_companies.json
Source: https://www.globiscapital.co.jp/en/companies — server-rendered list rows:
company name, description, initial investment month, stage at entry
(Seed/Early/Growth...), category (Business/Consumer/Frontier...) and website.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

ORIGIN = "https://www.globiscapital.co.jp"
SOURCE_URL = ORIGIN + "/en/companies"
PRIMARY = "Globis Capital Partners"
SECTOR_MAP = {"consumer": ["Consumer"]}
DATE = re.compile(r"^(January|February|March|April|May|June|July|August|September|October|November|December) (\d{4})$")
STAGES = {"seed", "early", "middle", "growth", "later", "late"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select('a[href^="/en/companies/"]'):
        st = [clean(t) for t in a.stripped_strings if clean(t)]
        if not st:
            continue
        row = a.parent.parent
        name, desc, date, stage, cat = st[0], None, None, None, None
        for t in st[1:]:
            if DATE.match(t):
                date = t
            elif t.lower() in STAGES:
                stage = t
            elif date and not cat:
                cat = t
            elif not desc:
                desc = t
        site = None
        for l in row.select("a[href^=http]"):
            if "globiscapital" not in l["href"] and not is_social(l["href"]):
                site = l["href"]
                break
        m = DATE.match(date or "")
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=[c.strip() for c in cat.split(",")] if cat else None, sector_map=SECTOR_MAP,
                       investment_date=date, first_invested_year=int(m.group(2)) if m else None,
                       stage_at_investment=stage, detail_url=ORIGIN + a["href"]))
    finish(out, "globis", ("description", "company_url", "first_invested_year", "stage_at_investment", "everywhere_tags"))


if __name__ == "__main__":
    main()
