#!/usr/bin/env python3
"""Avenir Growth Capital portfolio scraper -> avenir_companies.json
Source: https://www.avenirgrowth.com/portfolio — Next.js page; each <li data-name>
carries the sector (enterprise/consumer) in its class list, a one-line description,
a "Realized" label for exits and the external website link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.avenirgrowth.com/portfolio"
PRIMARY = "Avenir Growth"
SECTOR_MAP = {"consumer": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for li in soup.select("li[data-name]"):
        cls = li.get("class") or []
        sectors = [c.capitalize() for c in ("enterprise", "consumer") if c in cls]
        d = li.select_one('[class*="portfolio_description"]')
        titles = li.select_one('[class*="portfolio_titles"]')
        realized = bool(titles and any(clean(s) == "Realized" for s in titles.stripped_strings))
        a = li.find("a", href=True)
        url = a["href"] if a and a["href"].startswith("http") else None
        out.append(rec(li["data-name"], clean(d.get_text(" ", strip=True)) if d else None, url, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sectors, sector_map=SECTOR_MAP, status="realized" if realized else "active",
                       spotlight="spotlight" in cls))
    finish(out, "avenir", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
