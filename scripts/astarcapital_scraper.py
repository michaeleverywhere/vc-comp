#!/usr/bin/env python3
"""A* portfolio scraper -> astarcapital_companies.json
Source: https://www.a-star.co/companies — the companies page: the full alphabetical list (company
name + website link) and the featured company cards (A*'s one-line description). Names A* marks
with "*" ("This investment was made prior to the formation of A*") keep that flag in
prior_to_astar (the asterisk itself is dropped from the name)."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.a-star.co/companies"
PRIMARY = "A*"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    desc = {}
    for c in s.select(".companies__company"):
        n = c.select_one(".companies__name")
        d = c.select_one(".companies__description")
        if n:
            desc[clean(n.get_text(" ", strip=True)).rstrip("*").strip().lower()] = clean(d.get_text(" ", strip=True)) if d else None
    out = []
    for a in s.select("a.companies__full-list-item"):
        raw = clean(a.get_text(" ", strip=True))
        if not raw:
            continue
        prior = raw.endswith("*")
        name = raw.rstrip("*").strip()
        url = a.get("href")
        if url and is_social(url):
            url = None
        out.append(rec(name, desc.get(name.lower()), url, PRIMARY, SOURCE_URL, scraped_at,
                       prior_to_astar=prior))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} A* companies")
    finish(out, "astarcapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
