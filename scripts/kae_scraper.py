#!/usr/bin/env python3
"""Kae Capital portfolio scraper -> kae_companies.json
Source: https://kae-capital.com/ — WP REST `investments` posts (name, category
taxonomies) plus each investment page for description, Year Founded, Year of
investment and the Kae team lead.
"""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_many, html_text, label_after, year_of
from _d50_common import rec, finish, wp_all, wp_terms, page_strings

ORIGIN = "https://kae-capital.com"
SOURCE_URL = "https://kae-capital.com/investments/"
PRIMARY = "Kae Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "investments")
    cats = {**wp_terms(ORIGIN, "main-category"), **wp_terms(ORIGIN, "investments-category")}
    pages = fetch_many([p["link"] for p in posts], workers=6, pause=0.1)
    out = []
    for p in posts:
        name = html_text(p["title"]["rendered"])
        strings, soup = page_strings(pages.get(p["link"]) or "")
        desc = None
        if "Year Founded" in strings:
            i = strings.index("Year Founded")
            if i > 0 and len(strings[i - 1]) > 40:
                desc = strings[i - 1]
        sectors = [cats[i] for i in (p.get("main-category") or []) + (p.get("investments-category") or []) if i in cats]
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors,
                       year_founded=year_of(label_after(strings, "Year Founded")),
                       first_invested_year=year_of(label_after(strings, "Year of investment")),
                       lead_partner=label_after(strings, "Kae Team")))
    finish(out, "kae", ("description", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
