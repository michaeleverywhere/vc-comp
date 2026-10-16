#!/usr/bin/env python3
"""Mercato Partners (venture) portfolio scraper -> mercato_companies.json
Source: https://mercatopartners.com/portfolio/ — Webflow CMS
`.portfolio-card` items: company name, location, synopsis and the modal's
hidden fields (website, fund, status, year invested, series).
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://mercatopartners.com/portfolio/"
PRIMARY = "Mercato Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".portfolio-card"):
        def f(cls):
            el = it.select_one(".card-modal-hidden-fields__" + cls)
            return clean(el.get_text(" ", strip=True)) if el and "w-dyn-bind-empty" not in (el.get("class") or []) else None
        nm = it.select_one(".person-card__heading-text")
        if not nm or not clean(nm.get_text()):
            continue
        a = it.select_one("a.card-modal-hidden-fields__external-url[href]")
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        loc = it.select_one(".person-card__title-text")
        syn = it.select_one(".person-card__synopsis-text")
        det = it.select_one("a.nest-collection-link[href]")
        st = f("status")
        out.append(rec(nm.get_text(" ", strip=True), syn.get_text(" ", strip=True) if syn else None, href, PRIMARY,
                       SOURCE_URL, scraped_at, location=clean(loc.get_text(" ", strip=True)) if loc else None,
                       fund=f("fund"), portfolio_status=st,
                       status={"active": "active", "exited": "exited", "acquired": "acquired"}.get((st or "").lower()),
                       year_invested=year_of(f("year-invested") or ""), series=f("series"),
                       detail_url=urljoin(SOURCE_URL, det["href"]) if det else None))
    finish(out, "mercato", ("description", "company_url", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
