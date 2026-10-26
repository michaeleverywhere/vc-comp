#!/usr/bin/env python3
"""Serent Capital portfolio scraper -> serentcapital_companies.json
Source: https://serentcapital.com/portfolio/ — Serent Capital (San Francisco / Austin), growth investor backing
founder-led software and tech-enabled services companies. The WordPress portfolio (REST post type
`portfolio_companies`) lists every company with its profile text, industry and status (Current / Realized)."""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text
from _d50_common import rec, finish, wp_all

SOURCE_URL = "https://serentcapital.com/portfolio/"
ORIGIN = "https://serentcapital.com"
PRIMARY = "Serent Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for p in wp_all(ORIGIN, "portfolio_companies"):
        ti = p.get("taxonomy_info") or {}
        inds = [x["label"] for x in ti.get("portfolio_company_industry") or []]
        sts = [x["label"] for x in ti.get("portfolio_company_status") or []]
        s0 = sts[0] if sts else None
        st = "exited" if s0 and s0.lower().startswith(("realiz", "former", "exit")) else ("active" if s0 and s0.lower() == "current" else None)
        out.append(rec(html_text(p["title"]["rendered"]), html_text((p.get("content") or {}).get("rendered") or ""), None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=inds, status=st, serent_status=s0,
                       company_profile_url=p.get("link")))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Serent companies")
    finish(out, "serentcapital", ("description", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
