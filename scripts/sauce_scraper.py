#!/usr/bin/env python3
"""Sauce.vc portfolio scraper -> sauce_companies.json
Source: https://sauce.vc/portfolio/ — WordPress portfolio grid (`.tlp-content`):
company name + website (h3 link), short description and fund category.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://sauce.vc/portfolio/"
PRIMARY = "Sauce.vc"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for c in soup.select(".tlp-content"):
        h = c.find("h3")
        if not h:
            continue
        a = h.find("a", href=True)
        href = a["href"] if a else ""
        d = c.select_one(".tlp-portfolio-sd")
        fund = None
        for li in c.select("li.tools"):
            lab = li.find("label")
            if lab and "categor" in lab.get_text().lower():
                lab.extract()
                fund = clean(li.get_text(" ", strip=True))
        out.append(rec(h.get_text(" ", strip=True), clean(d.get_text(" ", strip=True)) if d else None,
                       href if href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at, fund=fund))
    finish(out, "sauce", ("description", "company_url", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
