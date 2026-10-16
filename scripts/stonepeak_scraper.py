#!/usr/bin/env python3
"""Stonepeak portfolio scraper -> stonepeak_companies.json
Source: https://stonepeak.com/investments — server-rendered expandable panels
(`.expandable-panel[id=<slug>-panel]`) with company name, HQ, investment date,
description and "Company website" link. Sector / region / realized status come
from the WP REST `company` post type's class_list term slugs, joined on slug.
"""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish, wp_all

ORIGIN = "https://stonepeak.com"
SOURCE_URL = ORIGIN + "/investments"
PRIMARY = "Stonepeak"
SECTOR_MAP = {"transportation & logistics": ["Logistics / Supply Chain", "Transportation / Mobility"],
              "energy transition renewables": ["Climate / Sustainability"]}
PRETTY = {"transportation-logistics": "Transportation & Logistics", "real-estate": "Real Estate"}


def pretty(slug):
    return PRETTY.get(slug) or " ".join(w.capitalize() for w in slug.split("-"))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    terms = {}
    for p in wp_all(ORIGIN, "company"):
        cl = p.get("class_list") or []
        g = lambda pre: [pretty(c[len(pre):]) for c in cl if c.startswith(pre)]
        terms[p["slug"]] = (g("sector-"), g("region-"), (g("company_status-") or [None])[0])
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for panel in soup.select(".expandable-panel[id$=-panel]"):
        slug = panel["id"][:-len("-panel")]
        nm = panel.select_one(".company__name")
        if not nm:
            continue
        meta = {}
        for li in panel.select(".company-panel__meta li"):
            k, sep, v = li.get_text(" ", strip=True).partition(":")
            if sep:
                meta[k.strip().lower()] = clean(v)
        desc = " ".join(p.get_text(" ", strip=True) for p in panel.select(".company-panel__content > p")) or None
        a = panel.select_one("a.company-panel__cta[href^=http]")
        site = a["href"] if a and not is_social(a["href"]) else None
        sec, reg, status = terms.get(slug, ([], [], None))
        out.append(rec(nm.get_text(" ", strip=True), desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sec, sector_map=SECTOR_MAP, hq_location=meta.get("headquarters"),
                       region=", ".join(reg) or None, investment_date=meta.get("investment date"),
                       first_invested_year=year_of(meta.get("investment date") or ""),
                       portfolio_status=status,
                       status={"unrealized": "active", "realized": "realized"}.get((status or "").lower()),
                       detail_url=f"{ORIGIN}/company/{slug}"))
    finish(out, "stonepeak", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
