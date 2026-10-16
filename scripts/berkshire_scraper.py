#!/usr/bin/env python3
"""Berkshire Partners private equity portfolio scraper -> berkshire_companies.json
Source: https://berkshirepartners.com/private-equity/portfolio/ — server-rendered
`.investments-item` cards whose classes carry current/former status, sector and
investment type; each card's detail page gives name, sector, location, year
invested, investment type, description and company website.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://berkshirepartners.com/private-equity/portfolio/"
PRIMARY = "Berkshire Partners"
SECTOR_MAP = {"healthcare": ["Health"], "consumer": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    cards = []
    for it in soup.select(".investments-item"):
        a = it.select_one("a[href*='/portfolio-companies/']")
        img = it.select_one("[aria-label]")
        if a:
            cards.append((a["href"], img.get("aria-label") if img else None, it.get("class", [])))
    pages = fetch_many([c[0] for c in cards])
    out = []
    for url, alt, cls in cards:
        d = BeautifulSoup(pages.get(url) or "", "html.parser")
        t = d.select_one(".investment-single-item--title")
        sector = None
        if t and t.small:
            sector = clean(t.small.get_text(" ", strip=True))
            t.small.extract()
        name = clean(t.get_text(" ", strip=True)) if t else alt
        meta = {clean(li.strong.get_text()).lower(): clean(li.span.get_text(" ", strip=True))
                for li in d.select(".investment-single-item--meta li") if li.strong and li.span}
        loc = d.select_one(".investment-single-item--location")
        if loc and loc.strong:
            loc.strong.extract()
        copy = d.select_one(".investment-single-item--copy")
        desc = " ".join(p.get_text(" ", strip=True) for p in copy.find_all("p") if "investment-single-item--link" not in (p.get("class") or [])) if copy else None
        link = d.select_one(".investment-single-item--link a[href]")
        site = link["href"] if link and not is_social(link["href"]) else None
        status = "Current" if "current" in cls else "Former" if "former" in cls else None
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sector] if sector else [], sector_map=SECTOR_MAP,
                       hq_location=clean(loc.get_text(" ", strip=True)) if loc else None,
                       first_invested_year=year_of(meta.get("year invested") or ""),
                       investment_type=meta.get("investment type"), portfolio_status=status,
                       status={"Current": "active", "Former": "realized"}.get(status), detail_url=url))
    finish(out, "berkshire", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
