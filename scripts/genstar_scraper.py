#!/usr/bin/env python3
"""Genstar Capital portfolio scraper -> genstar_companies.json
Source: https://www.gencap.com/companies/ — server-rendered company popups
(`.popup-content-box`): name (h2), description paragraphs, website link,
"Status: Current / 2024 Investment" and "Sector:" lines.
"""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.gencap.com/companies/"
PRIMARY = "Genstar Capital"
SECTOR_MAP = {"healthcare": ["Health"], "financial services": ["FinTech / Insurance"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for box in soup.select(".popup-content-box"):
        h2 = box.find("h2")
        if not h2:
            continue
        site = next((a["href"] for a in box.select("a[href^=http]") if "gencap.com" not in a["href"] and not is_social(a["href"])), None)
        desc = " ".join(p.get_text(" ", strip=True) for p in box.select(".text > p") if not p.find("a")) or None
        st = box.select_one(".status")
        st = clean(st.get_text(" ", strip=True).split(":", 1)[-1]) if st else None
        status = clean((st or "").split("/")[0]) or None
        sec = box.select_one(".sector")
        sec = clean(sec.get_text(" ", strip=True).split(":", 1)[-1]) if sec else None
        m = re.search(r"(\d{4})\s+Investment", st or "")
        out.append(rec(h2.get_text(" ", strip=True), desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[x for x in re.split(r"\s*/\s*", sec or "") if x], sector_map=SECTOR_MAP, portfolio_status=status,
                       status={"current": "active", "past": "realized"}.get((status or "").lower()),
                       first_invested_year=int(m.group(1)) if m else None))
    finish(out, "genstar", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
