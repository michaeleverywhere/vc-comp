#!/usr/bin/env python3
"""Hellman & Friedman portfolio scraper -> hf_companies.json
Source: https://hf.com/portfolio/ — WP REST `portfolio` (company name, content =
H&F's investment description) with people-sector, company-status (Current/Past)
and geography taxonomies; website taken from the first external link in content.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text, is_social, year_of
from _d50_common import rec, finish, wp_all, wp_terms

ORIGIN = "https://hf.com"
SOURCE_URL = ORIGIN + "/portfolio/"
PRIMARY = "Hellman & Friedman"
SECTOR_MAP = {"healthcare": ["Health"], "financial services": ["FinTech / Insurance"], "consumer services & retail": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    sec, stat, geo = wp_terms(ORIGIN, "people-sector"), wp_terms(ORIGIN, "company-status"), wp_terms(ORIGIN, "geography")
    out = []
    for p in wp_all(ORIGIN, "portfolio"):
        t = lambda m, k: [m[i] for i in p.get(k) or [] if i in m]
        html = p.get("content", {}).get("rendered") or ""
        soup = BeautifulSoup(html, "html.parser")
        site = next((a["href"] for a in soup.select("a[href^=http]") if "hf.com" not in a["href"] and not is_social(a["href"])), None)
        status = (t(stat, "company-status") or [None])[0]
        desc = html_text(html) or None
        out.append(rec(html_text(p["title"]["rendered"]), desc, site, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=t(sec, "people-sector"), sector_map=SECTOR_MAP, region=", ".join(t(geo, "geography")) or None,
                       portfolio_status=status, status={"current": "active", "past": "realized"}.get((status or "").lower()),
                       first_invested_year=year_of(desc[:20]) if desc and desc.startswith("In ") else None,
                       detail_url=p.get("link")))
    finish(out, "hf", ("description", "company_url", "status", "first_invested_year", "everywhere_tags"))


if __name__ == "__main__":
    main()
