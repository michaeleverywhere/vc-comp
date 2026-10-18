#!/usr/bin/env python3
"""Forward Venture Capital portfolio scraper -> forwardvc_companies.json
Source: https://forwardvc.com/ — Webflow one-pager: the "Current journeys" grid
(company name, city/country, website) and the "Past journeys" grid (name, city;
status exited). The third grid ("Our Team") is people and is skipped."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://forwardvc.com/"
PRIMARY = "Forward Venture Capital"


def label(grid):
    p = grid
    for _ in range(8):
        p = p.find_previous(string=True)
        t = clean(p) if p else None
        if t and t.lower().endswith("journeys."):
            return t.lower()
        if t and t.lower().startswith("our team"):
            return "team"
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for t in s(["script", "style"]):
        t.decompose()
    out = []
    for g in s.select(".portfolio-grid"):
        lab = label(g)
        if lab not in ("current journeys.", "past journeys."):
            continue
        for c in g.select(".portfolio-exit, .portfolio-card-exit"):
            n = c.select_one(".portfolio-name")
            name = clean(n.get_text(" ", strip=True)) if n else None
            if not name:
                continue
            city = c.select_one(".portfolio-city")
            a = c.select_one("a[href^=http]")
            loc = clean(city.get_text(" ", strip=True)) if city else None
            out.append(rec(name, None, a["href"] if a and not is_social(a["href"]) else None, PRIMARY, SOURCE_URL,
                           scraped_at, location=loc.title() if loc and loc == loc.lower() else loc,
                           portfolio_group="Current" if lab.startswith("current") else "Past",
                           status="active" if lab.startswith("current") else "exited"))
    finish(out, "forwardvc", ("company_url", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
