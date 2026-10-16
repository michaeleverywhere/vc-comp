#!/usr/bin/env python3
"""Alta Partners portfolio scraper -> alta_companies.json
Source: https://www.altapartners.com/portfolio — Foundation reveal modals per
company: name, location, website, industry, status, fund, bio.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.altapartners.com/portfolio"
PRIMARY = "Alta Partners"
SECTOR_MAP = {"life sciences": ["BioTech", "Health"], "biotechnology": ["BioTech", "Health"],
              "medical devices": ["Health"], "healthcare": ["Health"], "healthcare services": ["Health"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for m in soup.select(".company-reveal"):
        nm = m.select_one(".company-name")
        if not nm:
            continue
        g = lambda sel: (lambda e: clean(e.get_text(" ", strip=True)) if e else None)(m.select_one(sel))
        a = m.select_one("a.website-link[href^=http]")
        ind = g(".fact.industry")
        st = (g(".fact.status") or "").lower()
        out.append(rec(nm.get_text(" ", strip=True), g(".bio"), a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[ind] if ind else [], sector_map=SECTOR_MAP, location=g(".location"), fund=g(".fact.fund"),
                       status_detail=g(".fact.status"),
                       status="active" if st == "private" else ("ipo" if st.startswith("public") else (st or None))))
    finish(out, "alta", ("description", "company_url", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
