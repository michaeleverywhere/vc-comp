#!/usr/bin/env python3
"""FJ Labs portfolio scraper -> fjlabs_companies.json
Source: https://www.fjlabs.com/portfolio — Webflow CMS list (paginated
`?<hash>_page=N`); each item has the company name linked to its website and
Finsweet filter fields: Active / Exited flags, Entry Stage, Entry Year,
Geography, Industry, Marketplace, Region. No descriptions are published.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.fjlabs.com/portfolio"
PRIMARY = "FJ Labs"
SECTOR_MAP = {"fintech & insurtech": ["FinTech / Insurance"], "proptech & home improvements": ["PropTech"],
              "digital health": ["Health"], "crypto & web3": ["Web3 / Crypto"], "logistics": ["Logistics / Supply Chain"],
              "mobility": ["Transportation / Mobility"], "gaming": ["Gaming / Media / Entertainment"],
              "ecommerce": ["Consumer"], "travel & lifestyle": ["Consumer"], "recruitment": ["Future of Work"],
              "agtech & climate": ["Climate / Sustainability"], "energy & solar": ["Climate / Sustainability"],
              "biotech": ["BioTech"], "frontier tech": ["Deeptech / Robotics / AR/VR"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".collection-item.w-dyn-item"):
            a = it.select_one("a.collection-item-name")
            if not a:
                continue
            f = {d["fs-cmsfilter-field"].lower(): clean(d.get_text(" ", strip=True))
                 for d in it.select("[fs-cmsfilter-field]") if d is not a}
            exited, active = f.get("exited") == "true", f.get("active") == "true"
            status = "exited" if exited else "active" if active else None
            href = a.get("href") or ""
            inds = [s.strip() for s in (f.get("industry") or "").split(",") if s.strip()]
            out.append(rec(a.get_text(" ", strip=True), None, href if href.startswith("http") and not is_social(href) else None,
                           PRIMARY, SOURCE_URL, scraped_at, sectors=inds, sector_map=SECTOR_MAP,
                           stage=f.get("entry stage"), first_invested_year=year_of(f.get("entry year") or ""),
                           hq_location=f.get("geography"), region=f.get("region"),
                           marketplace={"yes": True, "no": False}.get((f.get("marketplace") or "").lower()),
                           portfolio_status=status.title() if status else None, status=status))
    finish(out, "fjlabs", ("company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
