#!/usr/bin/env python3
"""Geodesic Capital portfolio scraper -> geodesic_companies.json
Source: https://geodesiccap.com/portfolio/ — WordPress flip cards
(`.portfolio-block__back`): company name + website link (h2 a), category
and one-line description.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://geodesiccap.com/portfolio/"
PRIMARY = "Geodesic Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".portfolio-block__back"):
        h = it.find("h2")
        if not h or not clean(h.get_text()):
            continue
        a = h.find("a", href=True)
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        cat = it.find("span")
        cat = clean(cat.get_text(" ", strip=True)) if cat else None
        p = it.find("p")
        out.append(rec(h.get_text(" ", strip=True), p.get_text(" ", strip=True) if p else None, href, PRIMARY,
                       SOURCE_URL, scraped_at, sectors=[cat] if cat else []))
    finish(out, "geodesic", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
