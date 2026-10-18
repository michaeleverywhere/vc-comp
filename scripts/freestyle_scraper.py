#!/usr/bin/env python3
"""Freestyle Capital portfolio scraper -> freestyle_companies.json
Source: https://freestyle.vc/companies — React single-page site; the grid is filled
from the site's own public, unauthenticated tRPC call `companies.list` (the exact
request the page makes): company name, description, website, Current / Acquired
status (Freestyle's own label), Freestyle category and deal-owner partner."""
import os, sys, json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://freestyle.vc/companies"
API = "https://freestyle.vc/api/trpc/companies.list?batch=1&input=%7B%220%22%3A%7B%22json%22%3Anull%7D%7D"
PRIMARY = "Freestyle Capital"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "health": ["Health"], "healthcare": ["Health"],
              "real estate": ["PropTech"], "proptech": ["PropTech"], "consumer": ["Consumer"],
              "climate": ["Climate / Sustainability"], "edtech": ["Future of Work"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    rows = fetch_response(API).json()[0]["result"]["data"]["json"]
    out = []
    for c in rows:
        name = clean(c.get("name"))
        if not name:
            continue
        st = clean(c.get("status")) or ""
        cat = clean(c.get("category"))
        out.append(rec(name, c.get("description"), c.get("websiteUrl"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[cat] if cat and cat.lower() != "other" else [], sector_map=SECTOR_MAP,
                       portfolio_label=st or None,
                       status={"current": "active", "acquired": "acquired"}.get(st.lower(), st.lower() or None)))
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} Freestyle companies")
    finish(out, "freestyle", ("description", "company_url", "portfolio_label", "everywhere_tags"))


if __name__ == "__main__":
    main()
