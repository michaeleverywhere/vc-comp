#!/usr/bin/env python3
"""Foundation Capital portfolio scraper -> foundationcapital_companies.json
Source: https://foundationcapital.com/portfolio — the Framer "Company Listing" list (JS-rendered;
read via headless Chrome, clicking the page's own "Load more" control until every company is
shown): company name (site-authored listing heading). The page publishes no descriptions,
websites or sectors in the list, so those fields stay empty."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean
from _d50_common import rec, finish
from _chrome_click import dom_loadmore

SOURCE_URL = "https://foundationcapital.com/portfolio"
PRIMARY = "Foundation Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = dom_loadmore(SOURCE_URL, count_js="document.querySelectorAll('[data-framer-name=\"Company Listing\"] h3').length")
    s = BeautifulSoup(html, "html.parser")
    out = []
    for c in s.select('[data-framer-name="Company Listing"]'):
        h = c.find("h3")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if name:
            out.append(rec(name, None, None, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 100:
        raise SystemExit(f"FATAL: only {len(out)} Foundation Capital companies (load-more incomplete?)")
    finish(out, "foundationcapital", ("everywhere_tags",))


if __name__ == "__main__":
    main()
