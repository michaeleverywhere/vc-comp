#!/usr/bin/env python3
"""K5 Global portfolio scraper -> k5_companies.json
Source: https://k5global.com/companies — Webflow CMS list (paginated) of
`a.example-company` cards: company name, website, and optional ticker /
acquisition text (empty-bound fields are skipped).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://k5global.com/companies"
PRIMARY = "K5 Global"


def txt(el):
    if not el or "w-dyn-bind-empty" in (el.get("class") or []):
        return None
    return clean(el.get_text(" ", strip=True))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    pages = webflow_pages(SOURCE_URL)
    pages = list(pages.values()) if isinstance(pages, dict) else pages
    out = []
    for html in pages:
        soup = BeautifulSoup(html, "html.parser")
        for e in soup.select(".w-condition-invisible"):
            e.decompose()
        for a in soup.select("a.example-company"):
            nm = txt(a.select_one(".company-title"))
            if not nm:
                continue
            href = a.get("href") or ""
            ticker, acq = txt(a.select_one(".ticker-text")), txt(a.select_one(".acquisition-text"))
            out.append(rec(nm, None, href if href.startswith("http") and not is_social(href) else None,
                           PRIMARY, SOURCE_URL, scraped_at, ticker=ticker, acquisition=acq,
                           status="public" if ticker else ("acquired" if acq else None)))
    finish(out, "k5", ("company_url", "ticker", "acquisition", "everywhere_tags"))


if __name__ == "__main__":
    main()
