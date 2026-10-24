#!/usr/bin/env python3
"""Soma Capital portfolio scraper -> somacapital_companies.json
Source: https://somacap.com/portfolio — Soma Capital, early-stage venture firm. The portfolio page's "All Companies"
view is fed by the site's own public tRPC endpoint (companies.getCompaniesInfiniteQueryWithFilters, 30 per page,
cursor-paginated); each item gives the company name, one-liner, website, region, sectors (primary first) and the
valuation bracket Soma displays (e.g. "+10b", "1-10b")."""
import os, sys, json, urllib.parse
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://somacap.com/portfolio"
API = "https://somacap.com/api/trpc/companies.getCompaniesInfiniteQueryWithFilters"
PRIMARY = "Soma Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, cursor, seen_cursors = [], None, set()
    for _ in range(200):
        inp = {"json": {"limit": 30, "cursor": cursor}}
        d = fetch(API + "?input=" + urllib.parse.quote(json.dumps(inp)), as_json=True)
        data = d["result"]["data"]["json"]
        for c in data.get("results") or []:
            name = clean(c.get("name"))
            if not name:
                continue
            secs = sorted(c.get("sectors") or [], key=lambda s: not s.get("primary"))
            out.append(rec(name, c.get("oneLiner"), c.get("website"), PRIMARY, SOURCE_URL, scraped_at,
                           sectors=[s.get("name") for s in secs if s.get("name")],
                           region=c.get("region"), valuation_bracket=c.get("valuation")))
        cursor = data.get("nextCursor")
        if not cursor or cursor in seen_cursors:
            break
        seen_cursors.add(cursor)
    if len(out) < 100:
        raise SystemExit(f"FATAL: only {len(out)} Soma Capital companies")
    finish(out, "somacapital", ("description", "company_url", "region", "everywhere_tags"))


if __name__ == "__main__":
    main()
