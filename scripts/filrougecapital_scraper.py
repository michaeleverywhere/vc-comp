#!/usr/bin/env python3
"""Fil Rouge Capital portfolio scraper -> filrougecapital_companies.json
Source: https://www.filrougecapital.com/portfolio — Fil Rouge Capital, Zagreb-based pre-seed/seed venture firm
("Capital for the Bold") investing in founders across Central & Eastern Europe through its FRC1-FRC3 funds.
The paginated Webflow portfolio grid lists every company with exit / RIP / unicorn badges; each company page gives the
name, website, year invested, sector, key people and a short description."""
import os, sys, re
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_many, webflow_pages, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.filrougecapital.com/portfolio"
PRIMARY = "Fil Rouge Capital"


def visible(el, cls):
    b = el.select_one(f"div.{cls}")
    return bool(b) and "w-condition-invisible" not in (b.get("class") or [])


def field(s, cls):
    e = s.select_one(f"div.{cls}")
    return clean(e.get_text(" ")) if e else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    cards = {}
    for html in webflow_pages(SOURCE_URL):
        soup = BeautifulSoup(html, "html.parser")
        for a in soup.select("a.portfolio_logo_wrapper[href]"):
            href = urljoin(SOURCE_URL, a["href"])
            if href in cards:
                continue
            status = "Closed" if visible(a, "rip_banner") else ("Exited" if visible(a, "exit_banner") else "Active")
            cards[href] = (clean(a.get("aria-label")), status, visible(a, "unicorn_banner"))
    pages = fetch_many(list(cards), workers=4)
    out, seen = [], set()
    for href, (label, status, unicorn) in cards.items():
        html = pages.get(href)
        s = BeautifulSoup(html, "html.parser") if html else None
        item = s.select_one("div.portfolio_detail_item") if s else None
        name = field(item, "portfolio_detail_title") if item else None
        name = name or label
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        site = desc = year = sector = people = None
        if item:
            w = item.select_one("a.portfolio_detail_title_wrapper[href^=http]")
            site = w["href"] if w else None
            year = field(item, "portfolio_detail_year")
            sector = field(item, "portfolio_detail_sector")
            people = field(item, "portfolio_detail_keypeople")
            d = s.select_one("p.portfolio_detail_shortdesc")
            desc = clean(d.get_text(" ")) if d else None
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, sectors=[sector] if sector else None,
                       status=status, unicorn=True if unicorn else None, sector=sector,
                       year_invested=year if year and re.fullmatch(r"(19|20)\d{2}", year) else None,
                       key_people=[p.strip() for p in people.split(",") if p.strip()] if people else None,
                       profile_url=href))
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} Fil Rouge companies")
    finish(out, "filrougecapital", ("description", "company_url", "sector", "year_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
