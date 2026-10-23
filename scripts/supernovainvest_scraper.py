#!/usr/bin/env python3
"""Supernova Invest portfolio scraper -> supernovainvest_companies.json
Source: https://supernovainvest.com/portefeuille/ — Supernova Invest, Paris deeptech venture capital firm; the
portfolio grid's own WordPress records (WP REST portfolio post type): company name plus Supernova's country,
sector and sub-sector taxonomy terms."""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text
from _d50_common import rec, finish, wp_all, wp_terms

SOURCE_URL = "https://supernovainvest.com/portefeuille/"
ORIGIN = "https://supernovainvest.com"
PRIMARY = "Supernova Invest"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "portfolio")
    country, sector, sub = wp_terms(ORIGIN, "country"), wp_terms(ORIGIN, "sector"), wp_terms(ORIGIN, "subsector")
    out = []
    for p in posts:
        name = html_text(p["title"]["rendered"])
        if not name:
            continue
        sectors = [sector[i] for i in p.get("sector") or [] if i in sector]
        subs = [sub[i] for i in p.get("subsector") or [] if i in sub]
        loc = [country[i] for i in p.get("country") or [] if i in country]
        out.append(rec(name, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors + subs,
                       location=", ".join(loc) or None))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Supernova Invest companies")
    finish(out, "supernovainvest", ("sectors", "location", "everywhere_tags"))


if __name__ == "__main__":
    main()
