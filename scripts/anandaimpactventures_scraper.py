#!/usr/bin/env python3
"""Ananda Impact Ventures portfolio scraper -> anandaimpactventures_companies.json
Source: https://ananda.vc/portfolio/ — Ananda Impact Ventures, Munich impact venture capital firm; every portfolio
company's own WordPress record (WP REST portfolio post type): name, tagline, description, website, headquarters,
founders/management, year in portfolio, Ananda fund (I-V), impact category and sector, and the "Exited" marker."""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, html_text, year_of
from _d50_common import rec, finish, wp_all, wp_terms

SOURCE_URL = "https://ananda.vc/portfolio/"
ORIGIN = "https://ananda.vc"
PRIMARY = "Ananda Impact Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    posts = wp_all(ORIGIN, "portfolio")
    cats, sect, fund = wp_terms(ORIGIN, "categories"), wp_terms(ORIGIN, "sector"), wp_terms(ORIGIN, "hf_cat_portfolio")
    out = []
    for p in posts:
        name = html_text(p["title"]["rendered"])
        if not name:
            continue
        mb = p.get("meta_box") or {}
        sectors = [sect[i] for i in p.get("sector") or [] if i in sect] + \
                  [cats[i] for i in p.get("categories") or [] if i in cats and cats[i] != "Other"]
        fterms = [fund[i] for i in p.get("hf_cat_portfolio") or [] if i in fund]
        exited = "Exited" in fterms
        url = clean(mb.get("portco_website_url"))
        if url and not url.startswith("http"):
            url = "https://" + url
        people = [clean(n) for n in mb.get("portfolio_company_profile_management_names") or [] if clean(n)]
        ptype = clean(mb.get("portfolio_company_profile_management_type"))
        fn = clean(mb.get("ananda_fund_invested"))
        out.append(rec(name, html_text(mb.get("portco_description_text") or "") or clean(mb.get("portco_tagline")),
                       url, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors,
                       tagline=clean(mb.get("portco_tagline")),
                       location=clean(mb.get("portfolio_company_profile_headquarters")),
                       first_invested=year_of(mb.get("in_portfolio_since")),
                       founders=people if ptype == "founders" else [],
                       management=people if ptype != "founders" else [],
                       fund=f"Fund {fn}" if fn else None,
                       status="exited" if exited else "active", profile_url=p.get("link")))
    if len(out) < 25:
        raise SystemExit(f"FATAL: only {len(out)} Ananda companies")
    finish(out, "anandaimpactventures", ("description", "company_url", "location", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
