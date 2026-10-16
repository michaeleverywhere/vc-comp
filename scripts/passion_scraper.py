#!/usr/bin/env python3
"""Passion Capital portfolio scraper -> passion_companies.json
Source: https://passioncapital.com/ — WP REST `fund-portfolio` posts (name,
one-line description, fund + industry taxonomies) plus each company page for
Status, Founded, Passion Initial Investment year and the website link.
"""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_many, html_text, label_after, year_of
from _d50_common import rec, finish, wp_all, wp_terms, page_strings, link_by_text

ORIGIN = "https://passioncapital.com"
SOURCE_URL = "https://passioncapital.com/portfolio/"
PRIMARY = "Passion Capital"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "enterprise": ["Future of Work"], "consumer": ["Consumer"],
              "health": ["Health"], "healthcare": ["Health"], "climate": ["Climate / Sustainability"],
              "marketplace": ["Consumer"], "developer tools": ["Dev Tools / Cloud"], "security": ["Cybersecurity"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "fund-portfolio")
    funds, inds = wp_terms(ORIGIN, "fund"), wp_terms(ORIGIN, "industry")
    pages = fetch_many([p["link"] for p in posts], workers=6, pause=0.1)
    out = []
    for p in posts:
        strings, soup = page_strings(pages.get(p["link"]) or "")
        st = label_after(strings, "Status")
        industries = [inds[i] for i in p.get("industry") or [] if i in inds]
        out.append(rec(html_text(p["title"]["rendered"]), html_text(p["content"]["rendered"]),
                       link_by_text(soup, "Visit Website"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=industries, sector_map=SECTOR_MAP,
                       fund=", ".join(funds[i] for i in p.get("fund") or [] if i in funds) or None,
                       status=st.lower() if st else None, year_founded=year_of(label_after(strings, "Founded")),
                       first_invested_year=year_of(label_after(strings, "Passion Initial Investment"))))
    finish(out, "passion", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
