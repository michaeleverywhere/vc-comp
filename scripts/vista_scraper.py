#!/usr/bin/env python3
"""Vista Equity Partners portfolio scraper -> vista_companies.json
Source: https://www.vistaequitypartners.com/about/companies/ — WP REST `company`
(name, industry, fund taxonomies) plus each company page: Year of Investment,
Status, Headquarters, Strategy, Industry. Site publishes no descriptions.
"""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text, year_of, fetch_many, label_after
from _d50_common import rec, finish, wp_all, wp_terms, page_strings

ORIGIN = "https://www.vistaequitypartners.com"
SOURCE_URL = "https://www.vistaequitypartners.com/about/companies/"
PRIMARY = "Vista Equity Partners"
SECTOR_MAP = {"financial services": ["FinTech / Insurance"], "healthcare": ["Health"], "health & life sciences": ["Health"],
              "real estate & construction": ["PropTech"], "public sector": ["RegTech/Gov/Legal"], "government": ["RegTech/Gov/Legal"],
              "legal": ["RegTech/Gov/Legal"], "security": ["Cybersecurity"], "supply chain & logistics": ["Logistics / Supply Chain"],
              "human capital management": ["Future of Work"], "education": ["Future of Work"], "data & analytics": ["Data & Analytics"],
              "infrastructure software": ["Dev Tools / Cloud"], "energy & utilities": ["Climate / Sustainability"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    inds, funds = wp_terms(ORIGIN, "industry"), wp_terms(ORIGIN, "fund")
    posts = wp_all(ORIGIN, "company")
    pages = fetch_many([p["link"] for p in posts], workers=6, pause=0.1)
    out = []
    for p in posts:
        st, _ = page_strings(pages.get(p["link"]) or "")
        status = (label_after(st, "Status") or "").lower() or None
        ind = [inds[i] for i in p.get("industry") or [] if i in inds]
        out.append(rec(html_text(p["title"]["rendered"]), html_text(p.get("content", {}).get("rendered") or "") or None, None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=ind, sector_map=SECTOR_MAP,
                       first_invested_year=year_of(label_after(st, "Year of Investment")),
                       portfolio_status=label_after(st, "Status"),
                       status={"current": "active", "realized": "realized", "former": "realized"}.get(status, status),
                       location=label_after(st, "Headquarters"),
                       strategy=label_after(st, "Strategy") or ", ".join(funds[i] for i in p.get("fund") or [] if i in funds) or None,
                       detail_url=p["link"]))
    finish(out, "vista", ("first_invested_year", "status", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
