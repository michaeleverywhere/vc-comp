#!/usr/bin/env python3
"""Investcorp portfolio scraper -> investcorp_companies.json
Source: https://www.investcorp.com/what-we-do/portfolio/ — server-rendered
`.portfolio-item` cards (name + detail link); each detail page gives the
company website (title link), location, year acquired and description.
The site does not publish current/realized status.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.investcorp.com/what-we-do/portfolio/"
PRIMARY = "Investcorp"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    for it in soup.select(".portfolio-item"):
        a = it.select_one(".portfolio-title a[href]")
        if a:
            cards.append((a["href"], a.get_text(" ", strip=True)))
    pages = fetch_many([c[0] for c in cards])
    out = []
    for url, name in cards:
        d = BeautifulSoup(pages.get(url) or "", "html.parser")
        for t in d(["header", "nav", "footer", "script", "style"]):
            if t.name != "header" or "entry-header" not in (t.get("class") or []):
                t.decompose()
        ta = d.select_one(".portfolio-title a[href^=http]")
        site = ta["href"] if ta and "investcorp.com" not in ta["href"] and not is_social(ta["href"]) else None
        loc = d.select_one(".portfolio-location")
        yr = d.select_one(".date_acquired .portfolio-number")
        desc = " ".join(p.get_text(" ", strip=True) for p in d.select("p")
                        if len(p.get_text(strip=True)) > 60 and not p.find_parent(class_="widget")) or None
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       hq_location=clean(loc.get_text(" ", strip=True)) if loc else None,
                       first_invested_year=year_of(yr.get_text() if yr else ""), detail_url=url))
    finish(out, "investcorp", ("description", "company_url", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
