#!/usr/bin/env python3
"""Fin Capital portfolio scraper -> fincapital_companies.json
Source: https://www.fin.capital/portfolio — Webflow CMS list (paginated); each
`.insight-item` carries Finsweet fields (sub-sector `category`, `stage`,
`status`) and a popup with the company name (h2) and description; website from
the popup's external link when present.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.fin.capital/portfolio"
PRIMARY = "Fin Capital"
SECTOR_MAP = {"embedded finance": ["FinTech / Insurance"], "insurtech": ["FinTech / Insurance"],
              "payments": ["FinTech / Insurance"], "wealthtech": ["FinTech / Insurance"], "lending": ["FinTech / Insurance"],
              "deeptech": ["Deeptech / Robotics / AR/VR"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        for it in BeautifulSoup(html, "html.parser").select(".insight-item.w-dyn-item"):
            pr = it.select_one(".popup-right")
            h = pr.find("h2") if pr else None
            if not h:
                continue
            f = {d["fs-list-field"]: clean(d.get_text(" ", strip=True)) for d in it.select("[fs-list-field]")}
            bio = pr.select_one(".w-richtext")
            site = next((a["href"] for a in it.select(".popup-modal a[href^=http]")
                         if "fin.capital" not in a["href"] and not is_social(a["href"])), None)
            st = f.get("status")
            out.append(rec(h.get_text(" ", strip=True), bio.get_text(" ", strip=True) if bio else None, site, PRIMARY,
                           SOURCE_URL, scraped_at, sectors=[f["category"]] if f.get("category") else [],
                           sector_map=SECTOR_MAP, stage=f.get("stage"), portfolio_status=st,
                           status={"active": "active", "exited": "exited", "acquired": "acquired"}.get((st or "").lower())))
    finish(out, "fincapital", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
