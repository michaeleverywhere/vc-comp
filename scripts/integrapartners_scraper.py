#!/usr/bin/env python3
"""Integra Partners portfolio scraper -> integrapartners_companies.json
Source: https://integrapartners.co/portfolio/ — Integra Partners (formerly Dymon Asia Ventures), Singapore
early-stage venture firm investing in Southeast Asia; the portfolio grid's own WordPress records (WP REST portfolio
post type): company name as Integra writes it, one-line description, website, and Integra's sector, impact-theme,
region and status (Active / Exited) terms."""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, html_text
from _d50_common import rec, finish, wp_all, wp_terms

SOURCE_URL = "https://integrapartners.co/portfolio/"
ORIGIN = "https://www.integrapartners.co"
PRIMARY = "Integra Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "portfolio")
    sector, theme = wp_terms(ORIGIN, "sector"), wp_terms(ORIGIN, "impact-theme")
    region, status = wp_terms(ORIGIN, "region"), wp_terms(ORIGIN, "portfolio-status")
    out = []
    for p in posts:
        name = html_text(p["title"]["rendered"])
        if not name:
            continue
        acf = p.get("acf") or {}
        st = [status[i] for i in p.get("portfolio-status") or [] if i in status]
        regions = [region[i] for i in p.get("region") or [] if i in region]
        out.append(rec(name, html_text((p.get("excerpt") or {}).get("rendered") or ""), clean(acf.get("website")),
                       PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sector[i] for i in p.get("sector") or [] if i in sector],
                       impact_themes=[theme[i] for i in p.get("impact-theme") or [] if i in theme],
                       markets=regions, status=st[0].lower() if st else None))
    if len(out) < 25:
        raise SystemExit(f"FATAL: only {len(out)} Integra Partners companies")
    finish(out, "integrapartners", ("description", "company_url", "sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
