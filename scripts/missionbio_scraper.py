#!/usr/bin/env python3
"""Mission BioCapital portfolio scraper -> missionbio_companies.json
Source: https://www.missionbiocapital.com/portfolio/ — logo-carousel modals
(`.sp-lcpro-modal-logo`): company name (h3), description paragraph and a
table with Industry, Status, Initial Investment and Visit (website).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.missionbiocapital.com/portfolio/"
PRIMARY = "Mission BioCapital"
SECTOR_MAP = {"therapeutics": ["BioTech"], "lab tools": ["BioTech"], "diagnostics": ["Health"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for m in soup.select(".sp-lcpro-modal-logo"):
        h = m.select_one(".lcpro-logo-title")
        if not h:
            continue
        d = m.select_one(".lcpro-description")
        f, site = {}, None
        for tr in (d.select("tr") if d else []):
            td = tr.find_all("td")
            if len(td) >= 2:
                k = (clean(td[0].get_text(" ", strip=True).replace(":", "")) or "").lower()
                f[k] = clean(td[1].get_text(" ", strip=True))
                a = td[1].find("a", href=True)
                if k == "visit" and a and a["href"].startswith("http") and not is_social(a["href"]):
                    site = a["href"]
        desc = " ".join(p.get_text(" ", strip=True) for p in d.find_all("p", recursive=False)) if d else None
        st = f.get("status")
        out.append(rec(h.get_text(" ", strip=True), desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[f["industry"]] if f.get("industry") else [], sector_map=SECTOR_MAP,
                       first_invested_year=year_of(f.get("initial investment") or ""), portfolio_status=st,
                       status={"active": "active", "exited": "exited", "current": "active"}.get((st or "").lower())))
    finish(out, "missionbio", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
