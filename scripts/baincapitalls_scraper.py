#!/usr/bin/env python3
"""Bain Capital Life Sciences portfolio scraper -> baincapitalls_companies.json
Source: https://www.baincapitallifesciences.com/portfolio — listing (name, year)
plus each company page: website, YEAR, STATUS (Current/Former), description.
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, label_after, year_of, is_social
from _d50_common import rec, finish, page_strings

SOURCE_URL = "https://www.baincapitallifesciences.com/portfolio"
PRIMARY = "Bain Capital Life Sciences"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    items = []
    for a in soup.select("#portfolio-listing a[href^='/portfolio/']"):
        h = a.select_one("h2")
        if h:
            sp = a.select_one("span")
            items.append((clean(h.get_text(" ", strip=True)), urljoin(SOURCE_URL, a["href"]),
                          year_of(sp.get_text(strip=True)) if sp else None))
    pages = fetch_many([i[1] for i in items], workers=6, pause=0.1)
    out = []
    for name, link, yr in items:
        st, s = page_strings(pages.get(link) or "")
        site = desc = None
        status_raw = label_after(st, "STATUS")
        if "STATUS" in st:
            i = st.index("STATUS") + 2
            if i < len(st) and len(st[i]) > 60:
                desc = st[i]
        for a in (s.select("a[href^=http]") if pages.get(link) else []):
            if "baincapital" not in a["href"] and not is_social(a["href"]):
                site = a["href"]; break
        sr = (status_raw or "").lower()
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=["Life Sciences"],
                       sector_map={"life sciences": ["BioTech", "Health"]},
                       first_invested_year=year_of(label_after(st, "YEAR")) or yr,
                       portfolio_status=status_raw,
                       status="active" if sr in ("current", "active") else ("exited" if sr == "former" else None), detail_url=link))
    finish(out, "baincapitalls", ("description", "company_url", "first_invested_year", "portfolio_status", "everywhere_tags"))


if __name__ == "__main__":
    main()
