#!/usr/bin/env python3
"""Inveready portfolio scraper -> inveready_companies.json
Source: https://inveready.com/portfolio/ — Inveready, Barcelona/Madrid venture capital firm (venture, life-sciences
and other platforms). Each portfolio tile carries a data-portfolio-detail JSON blob with the company name, website and
fields Status / Platform / Year invested. Holdings only in Inveready's Private Equity and/or Infrastructure platforms
(no Venture or Life Sciences platform) are buyout-style and skipped (VC-only rule)."""
import json, os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://inveready.com/portfolio/"
PRIMARY = "Inveready"
VC_PLATFORMS = {"venture", "life sciences"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select("a.portfolio__item[data-portfolio-detail]"):
        try:
            d = json.loads(a["data-portfolio-detail"])
        except ValueError:
            continue
        name = clean(d.get("title"))
        if not name:
            continue
        f = {clean(x.get("label")): clean(x.get("value")) for x in d.get("fields") or [] if x.get("label")}
        platforms = [p.strip() for p in (f.get("Platform") or "").split(",") if p.strip()]
        if platforms and not any(p.lower() in VC_PLATFORMS for p in platforms):
            continue
        status = (f.get("Status") or "").lower() or None
        out.append(rec(name, None, d.get("url"), PRIMARY, SOURCE_URL, scraped_at,
                       inveready_platforms=platforms, fund=f.get("Fund"),
                       year_invested=f.get("Year invested"),
                       status="exited" if status == "exited" else status,
                       profile_url=d.get("permalink")))
    if len(out) < 100:
        raise SystemExit(f"FATAL: only {len(out)} Inveready companies")
    finish(out, "inveready", ("company_url", "year_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
