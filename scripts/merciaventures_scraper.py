#!/usr/bin/env python3
"""Mercia Ventures portfolio scraper -> merciaventures_companies.json
Source: https://www.mercia.co.uk/portfolio/ — Mercia (Mercia Asset Management, Henley-in-Arden / UK regions), regional
venture capital investor backing early-stage and growth companies across the UK. The WordPress portfolio (REST post type
`portfolio`) lists every company with a short description and its sector, fund, investment-type and status
(Realised / Unrealised / Partially realised) taxonomies. Companies held only through Mercia's debt, loan, mezzanine,
real-estate or private-equity funds are skipped so the dataset stays venture/equity investments."""
import os, sys, re
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text
from _d50_common import rec, finish, wp_all, wp_terms

SOURCE_URL = "https://www.mercia.co.uk/portfolio/"
ORIGIN = "https://www.mercia.co.uk"
PRIMARY = "Mercia Ventures"
NON_EQUITY = re.compile(r"debt|loan|mezzanine|real estate|cbils|private equity", re.I)
STATUS = {"realised": "exited", "unrealised": "active", "partially realised": "active"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    sec, fund, st, inv = (wp_terms(ORIGIN, t) for t in ("sector", "fund_type", "status", "investment_type"))
    out = []
    for p in wp_all(ORIGIN, "portfolio"):
        funds = [fund.get(i) for i in p.get("fund_type") or [] if fund.get(i)]
        if funds and all(NON_EQUITY.search(f) for f in funds):
            continue
        name = html_text(p["title"]["rendered"])
        name = re.sub(r"\s+(Ltd\.?|Limited|PLC|plc)$", "", name).strip()
        desc = html_text((p.get("content") or {}).get("rendered") or "")
        sectors = [sec[i] for i in p.get("sector") or [] if sec.get(i) and not re.search(r"board|operations|mercia|fdc", sec[i], re.I)]
        status = [st[i] for i in (p.get("status") if isinstance(p.get("status"), list) else []) if st.get(i)]
        s0 = status[0] if status else None
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors,
                       status=STATUS.get((s0 or "").lower()), mercia_status=s0,
                       mercia_funds=funds, investment_type=", ".join(inv[i] for i in p.get("investment_type") or [] if inv.get(i)) or None,
                       company_profile_url=p.get("link")))
    if len(out) < 150:
        raise SystemExit(f"FATAL: only {len(out)} Mercia companies")
    finish(out, "merciaventures", ("description", "sectors", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
