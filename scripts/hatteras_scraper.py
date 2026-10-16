#!/usr/bin/env python3
"""Hatteras Venture Partners portfolio scraper -> hatteras_companies.json
Source: https://hatterasvp.com/portfolio/ — server-rendered (WordPress) grid;
each company block links to /hvp_portfolio/<slug>/ with the company name in
the link title, followed by a one-paragraph description.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://hatterasvp.com/portfolio/"
PRIMARY = "Hatteras Venture Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, seen = [], set()
    for a in soup.select("a[href*='/hvp_portfolio/'][title]"):
        href = a["href"]
        if href in seen:
            continue
        seen.add(href)
        desc = None
        for sib in a.find_next_siblings():
            if sib.name == "a" and "/hvp_portfolio/" in (sib.get("href") or "") and sib["href"] != href:
                break
            p = sib.find("p")
            if p and clean(p.get_text(" ", strip=True)):
                desc = p.get_text(" ", strip=True)
                break
        out.append(rec(a["title"], desc, None, PRIMARY, SOURCE_URL, scraped_at, detail_url=href))
    finish(out, "hatteras", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
