#!/usr/bin/env python3
"""HealthCap portfolio scraper -> healthcap_companies.json
Source: https://www.healthcap.eu/portfolio/ — server-rendered "Portfolio
Companies" panel (`#panel-companies .hc-portfolio-page__item`, whose
data-hc-filter-value is true for current / false for former holdings) joined
to each company's overlay dialog (name, description, Country, Website).
The "Approved Products" panel is excluded.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.healthcap.eu/portfolio/"
PRIMARY = "HealthCap"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select("#panel-companies .hc-portfolio-page__item"):
        a = it.select_one("a[aria-controls]")
        ov = soup.find(id=a["aria-controls"]) if a else None
        if not ov:
            continue
        info = {}
        site = None
        for row in ov.select(".hc-overlay__info__row"):
            lab = clean(row.select_one(".hc-overlay__info__row__label").get_text())
            val = row.select_one(".hc-overlay__info__row__value")
            info[(lab or "").lower()] = clean(val.get_text(" ", strip=True))
            l = val.find("a", href=True)
            if (lab or "").lower() == "website" and l and l["href"].startswith("http") and not is_social(l["href"]):
                site = l["href"]
        cur = it.get("data-hc-filter-value")
        status = {"true": "Current", "false": "Former"}.get(cur)
        h = ov.select_one(".hc-overlay__heading")
        t = ov.select_one(".hc-overlay__text")
        out.append(rec(h.get_text(" ", strip=True) if h else a.get_text(" ", strip=True),
                       t.get_text(" ", strip=True) if t else None, site, PRIMARY, SOURCE_URL, scraped_at,
                       hq_location=info.get("country"), portfolio_status=status,
                       status={"Current": "active", "Former": "exited"}.get(status)))
    finish(out, "healthcap", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
