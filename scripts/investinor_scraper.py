#!/usr/bin/env python3
"""Investinor portfolio scraper -> investinor_companies.json
Source: https://investinor.no/en/portfolio/ — Investinor, Norway's state-owned venture capital investor; the MixItUp
portfolio grid lists each holding with Investinor's one-paragraph description, website and filter classes for
industry, Norwegian county and portfolio group (Companies / Exits). Fund-of-fund commitments (group "Funds",
industry "Fund") are not companies and are skipped."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url
from _d50_common import rec, finish

SOURCE_URL = "https://investinor.no/en/portfolio/"
PRIMARY = "Investinor"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    groups = {}
    for fs in soup.select("fieldset[data-filter-group]"):
        groups[fs["data-filter-group"]] = {i["value"].lstrip("."): clean(i.parent.get_text(" ", strip=True))
                                           for i in fs.select("input[value]")}
    ind, geo, inv = groups.get("industry", {}), groups.get("geography", {}), groups.get("investment", {})
    out = []
    for art in soup.select("article.portfolio-card"):
        cls = set(art.get("class", []))
        if "fund" in cls or "fondsportefolje-en" in cls:
            continue
        h = art.select_one("h2")
        name = clean(h.get_text(" ", strip=True)) if h else None
        if not name:
            continue
        p = art.select_one("div.align-inner > p")
        a = art.select_one("a.wrapper-link[href]")
        sectors = [ind[c] for c in cls if c in ind and ind[c]]
        county = next((geo[c] for c in cls if c in geo), None)
        location = None if not county or county == "Abroad" else f"{county}, Norway"
        exited = "avhendet-portefolje-en" in cls
        out.append(rec(name, clean(p.get_text(" ", strip=True)) if p else None, clean_url(a["href"]) if a else None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=sorted(sectors), location=location,
                       portfolio_group=next((inv[c] for c in cls if c in inv), None),
                       status="exited" if exited else "active"))
    if len(out) < 90:
        raise SystemExit(f"FATAL: only {len(out)} Investinor companies")
    finish(out, "investinor", ("description", "company_url", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
