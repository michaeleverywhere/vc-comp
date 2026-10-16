#!/usr/bin/env python3
"""Dell Technologies Capital portfolio scraper -> delltech_companies.json
Source: https://www.delltechnologiescapital.com/companies — Webflow CMS list
(paginated) `.companies_collection-item`: name (fs-cmsfilter-field="name"),
status (Active / "Acquired by X" / ticker), focus areas, DTC lead, region and
first investment year (Finsweet fields). Conditionally-hidden elements are
dropped before parsing.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.delltechnologiescapital.com/companies"
PRIMARY = "Dell Technologies Capital"
SECTOR_MAP = {"infrastructure": ["Dev Tools / Cloud"], "enterprise software": ["Dev Tools / Cloud"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    pages = webflow_pages(SOURCE_URL)
    pages = list(pages.values()) if isinstance(pages, dict) else pages
    out = []
    for html in pages:
        soup = BeautifulSoup(html, "html.parser")
        for e in soup.select(".w-condition-invisible"):
            e.decompose()
        for it in soup.select(".companies_collection-item"):
            nm = it.select_one("[fs-cmsfilter-field='name']")
            if not nm:
                continue
            cw = it.select_one(".content_wrapper")
            status_txt = None
            if cw:
                strs = list(cw.stripped_strings)
                if strs and strs[0] == "Status" and len(strs) > 1:
                    status_txt = clean(strs[1])
            def field(k):
                vals = []
                for e in (cw or it).select(f"[fs-cmsfilter-field='{k}']"):
                    v = clean(e.get_text(" ", strip=True))
                    if v and v not in vals:
                        vals.append(v)
                return vals
            low = (status_txt or "").lower()
            status = ("active" if low == "active" else "exited" if low == "exited" else "acquired" if low.startswith("acquired")
                      else "public" if (low.startswith("nasdaq") or low.startswith("nyse")) else None)
            out.append(rec(nm.get_text(" ", strip=True), None, None, PRIMARY, SOURCE_URL, scraped_at,
                           sectors=field("area"), sector_map=SECTOR_MAP, portfolio_status=status_txt, status=status,
                           lead=", ".join(field("lead")) or None, region=", ".join(field("region")) or None,
                           first_invested_year=year_of(" ".join(field("first-investment")))))
    finish(out, "delltech", ("status", "region", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
