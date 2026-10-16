#!/usr/bin/env python3
"""Vendep Capital portfolio scraper -> vendep_companies.json
Source: https://www.vendep.com/portfolio — Webflow/Finsweet table rows: logo alt
(name), one-liner, stage, fund, status; accordion with year, latest funding,
website and long description.
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, stage_label, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.vendep.com/portfolio"
PRIMARY = "Vendep Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".folio-table_item.w-dyn-item"):
        img = it.select_one("img.folio-table_logo[alt]")
        name = clean(re.sub(r"\s*logo$", "", img.get("alt") or "", flags=re.I)) if img else None
        if not name:
            continue
        g = lambda f: (lambda e: clean(e.get_text(" ", strip=True)) if e else None)(it.select_one(f'[fs-list-field="{f}"]'))
        one = it.select_one(".is-description .folio-table_text")
        acc = {}
        for w in it.select(".folio-table_accordion-text-wrapper"):
            tag = w.select_one(".text-style-tag")
            if not tag:
                continue
            k = clean(tag.get_text()).lower()
            if k == "website":
                a = w.select_one("a[href^=http]")
                acc[k] = a["href"] if a else None
            else:
                acc[k] = clean(w.get_text(" ", strip=True)[len(tag.get_text()):])
        stage = g("stage")
        st = (g("status") or "").lower()
        out.append(rec(name, acc.get("description") or (one.get_text(" ", strip=True) if one else None), acc.get("website"),
                       PRIMARY, SOURCE_URL, scraped_at, tagline=clean(one.get_text(" ", strip=True)) if one else None,
                       stage=stage_label(stage), stage_raw=stage, fund=g("fund"), status=st or None,
                       first_invested_year=year_of(acc.get("year")), latest_funding=acc.get("latest funding")))
    finish(out, "vendep", ("description", "company_url", "stage", "status", "first_invested_year", "latest_funding", "everywhere_tags"))


if __name__ == "__main__":
    main()
