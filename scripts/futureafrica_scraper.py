#!/usr/bin/env python3
"""Future Africa portfolio scraper -> futureafrica_companies.json
Source: https://www.future.africa/companies — Webflow CMS list (paginated) of
`.company-item` cards: company name (h5.company-industry, matching the logo
alt) and portfolio status (h5.company-active: Active, Full Exits, ...).
Names and status only.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.future.africa/companies"
PRIMARY = "Future Africa"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    pages = webflow_pages(SOURCE_URL)
    pages = list(pages.values()) if isinstance(pages, dict) else pages
    out = []
    for html in pages:
        soup = BeautifulSoup(html, "html.parser")
        for e in soup.select(".w-condition-invisible"):
            e.decompose()
        for it in soup.select(".company-item"):
            nm = it.select_one(".company-industry")
            if not nm or not clean(nm.get_text()):
                continue
            st = it.select_one(".company-active")
            st = clean(st.get_text(" ", strip=True)) if st else None
            low = (st or "").lower()
            out.append(rec(nm.get_text(" ", strip=True), None, None, PRIMARY, SOURCE_URL, scraped_at,
                           portfolio_status=st,
                           status="active" if low == "active" else ("exited" if low.startswith("full exit") else None)))
    finish(out, "futureafrica", ("status", "everywhere_tags"))


if __name__ == "__main__":
    main()
