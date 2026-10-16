#!/usr/bin/env python3
"""Manhattan Venture Partners portfolio scraper -> mvp_companies.json
Source: https://www.mvp.vc/portfolio — Webflow CMS list `.portfolio_item`;
company name is the CMS name field (h3.portfolio_name, shown when no logo),
each linking to /companies/<slug>. Names and detail pages only.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch
from _d50_common import rec, finish

SOURCE_URL = "https://www.mvp.vc/portfolio"
PRIMARY = "Manhattan Venture Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".portfolio_item"):
        h = it.select_one(".portfolio_name")
        a = it.select_one("a[href]")
        if not h:
            continue
        out.append(rec(h.get_text(" ", strip=True), None, None, PRIMARY, SOURCE_URL, scraped_at,
                       detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "mvp", ("detail_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
