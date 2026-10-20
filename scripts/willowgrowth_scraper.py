#!/usr/bin/env python3
"""Willow Growth Partners portfolio scraper -> willowgrowth_companies.json
Source: https://willowgrowth.com/brands/ — the brands grid's own WordPress records
(portfolio posts via WP REST, the same records the filterable grid loads): brand name, Willow's
one-line tagline, description and Willow's category (Beauty / Family / Food & Bev / ...)."""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, html_text
from _d50_common import rec, finish, wp_all, wp_terms

SOURCE_URL = "https://willowgrowth.com/brands/"
ORIGIN = "https://willowgrowth.com"
PRIMARY = "Willow Growth Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    cats = wp_terms(ORIGIN, "portfolio_category")
    out = []
    for p in wp_all(ORIGIN, "portfolio"):
        name = clean(html_text(p["title"]["rendered"]))
        if not name:
            continue
        desc = clean(html_text(p.get("content", {}).get("rendered") or ""))
        tag = clean(html_text(p.get("excerpt", {}).get("rendered") or ""))
        out.append(rec(name, desc or tag, None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[cats[c] for c in p.get("portfolio_category") or [] if c in cats],
                       tagline=tag if desc else None))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Willow companies")
    finish(out, "willowgrowth", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
