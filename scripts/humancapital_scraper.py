#!/usr/bin/env python3
"""Human Capital portfolio scraper -> humancapital_companies.json
Source: https://human.capital/portfolio — Webflow list: company name and the link
Human Capital gives for it (usually the company website). No descriptions.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import webflow_pages, clean
from _d50_common import rec, finish

SOURCE_URL = "https://human.capital/portfolio"
PRIMARY = "Human Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for it in soup.select(".portfolio-company"):
            h = it.select_one(".portfolio-company-header")
            if not h or not clean(h.get_text()):
                continue
            a = it.select_one("a[href^=http]")
            out.append(rec(h.get_text(" ", strip=True), None, a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "humancapital", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
