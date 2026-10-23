#!/usr/bin/env python3
"""500 Global portfolio scraper -> 500global_companies.json
Source: https://500.co/portfolio — 500 Global (formerly 500 Startups), global seed / early-stage venture capital firm;
the portfolio page is fed by the site's own public JSON route (https://500.co/api/startups): company (business) name
and legal name, one-liner, website, founders, country / region of operation, business model, the firm's industry
labels, current stage label (Pre-Seed / Seed / Series A-D / Exited / Dissolved), 500 programme batch(es), regional
fund tenants and initial investment date(s)."""
import os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, stage_label
from _d50_common import rec, finish

SOURCE_URL = "https://500.co/portfolio"
API = "https://500.co/api/startups"
PRIMARY = "500 Global"


def url_of(u):
    u = clean(u)
    if not u:
        return None
    return u if re.match(r"(?i)https?://", u) else "https://" + u.lstrip("/")


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    data = fetch(API, as_json=True)["res"]
    out = []
    for s in data:
        o = s.get("organization") or {}
        name = clean(o.get("businessName")) or clean(o.get("name"))
        if not name:
            continue
        st = clean((s.get("stage") or {}).get("name"))
        status = "exited" if st in ("Exited", "Secondary Sale") else ("closed" if st == "Dissolved" else "active")
        dates = sorted(d[:10] for d in (i.get("initialInvestDate") for i in s.get("investments") or []) if d)
        founders = [clean(f"{(p.get('person') or {}).get('firstName') or ''} {(p.get('person') or {}).get('lastName') or ''}")
                    for p in o.get("positions") or []]
        country = clean((o.get("countryOfOperation") or {}).get("name"))
        region = clean((o.get("regionOfOperation") or {}).get("name"))
        out.append(rec(name, clean(s.get("oneLiner")), url_of(o.get("companyUrl")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[clean(x.get("name")) for x in s.get("industries") or [] if clean(x.get("name"))],
                       legal_name=clean(o.get("name")) if clean(o.get("name")) != name else None,
                       founders=[f for f in founders if f], location=country.title() if country and country.isupper() else country,
                       region=region, business_model=clean((s.get("businessModel") or {}).get("name")),
                       stage_label_raw=st, stage=stage_label(st) if st and st not in ("Exited", "Secondary Sale") else None,
                       first_invested=dates[0] if dates else None, investment_dates=dates,
                       batches=[clean(b.get("brandName")) for b in s.get("batches") or [] if clean(b.get("brandName"))],
                       fund_tenants=[t.get("slug") for t in s.get("tenant") or [] if t.get("slug")],
                       status=status))
    if len(out) < 1500:
        raise SystemExit(f"FATAL: only {len(out)} 500 Global companies")
    finish(out, "500global", ("description", "company_url", "location", "stage", "first_invested", "everywhere_tags"))


if __name__ == "__main__":
    main()
