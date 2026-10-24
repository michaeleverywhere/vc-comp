#!/usr/bin/env python3
"""Gold House Ventures portfolio scraper -> goldhouseventures_companies.json
Source: https://goldhouse.org/ghv-companies/ — Gold House Ventures, the early-stage venture fund of Gold House
investing in startups led by Asian Pacific founders. Each portfolio card gives the company name, one-line
description, website, sector category and fund (Fund I / Fund II)."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://goldhouse.org/ghv-companies/"
PRIMARY = "Gold House Ventures"
CAT = {"ai-ml": "AI/ML", "b2b-saas": "B2B SaaS", "consumer": "Consumer", "cpg": "CPG",
       "fintech": "Fintech", "healthcare": "Healthcare"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select("div.portfolio-companies__item"):
        h = it.select_one(".card-portfolio-inline__title")
        name = clean(h.get_text(" ")) if h else None
        if not name:
            continue
        sub = it.select_one(".card-portfolio-inline__subtitle")
        a = it.select_one("a.card-portfolio-inline[href]")
        cat = it.get("data-company-category")
        href = a.get("href") if a else None
        if href and ("google.com/" in href or "goldhouse.org" in href):
            href = None  # redirect / self links are not the company website
        out.append(rec(name, clean(sub.get_text(" ")) if sub else None, href,
                       PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[CAT.get(cat, cat)] if cat else None, fund=clean(it.get("data-company-fund"))))
    if len(out) < 25:
        raise SystemExit(f"FATAL: only {len(out)} Gold House Ventures companies")
    finish(out, "goldhouseventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
