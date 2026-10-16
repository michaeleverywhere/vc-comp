#!/usr/bin/env python3
"""N49P portfolio scraper -> n49p_companies.json
Source: https://www.n49p.com/portfolio — Webflow/Finsweet list (paginated
?<hash>_page=N): name, description, status (Active/Exited), city, website.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, webflow_pages
from _d50_common import rec, finish

SOURCE_URL = "https://www.n49p.com/portfolio"
PRIMARY = "N49P"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    items = []
    for html in webflow_pages(SOURCE_URL):
        items += BeautifulSoup(html, "html.parser").select(".portfolio-item.w-dyn-item")
    out = []
    for it in items:
        h3 = it.select_one("h3")
        if not h3:
            continue
        p = it.select_one(".div-block-8 p")
        status = None
        for tag in it.select(".portfolio-tag"):
            if "w-condition-invisible" in (tag.get("class") or []):
                continue
            s = tag.select_one('[fs-cmsfilter-field="status"]')
            status = clean(s.get_text()) if s else None
        city = it.select_one(".status-url p.text-weight-bold")
        a = it.select_one(".status-url a[href^=http]")
        out.append(rec(h3.get_text(" ", strip=True), p.get_text(" ", strip=True) if p else None, a["href"] if a else None,
                       PRIMARY, SOURCE_URL, scraped_at, location=clean(city.get_text()) if city else None,
                       status=(status or "").lower() or None))
    finish(out, "n49p", ("description", "company_url", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
