#!/usr/bin/env python3
"""Kindred Capital portfolio scraper -> kindredcapital_companies.json
Source: https://kindred-portfolio-api.vercel.app/api/companies (CSV linked from kindredcapital.vc).
"""
import csv, io, json, os, sys
from datetime import datetime, timezone

import requests

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean, HEADERS, TIMEOUT

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://kindredcapital.vc/portfolio"
API_URL = "https://kindred-portfolio-api.vercel.app/api/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "kindredcapital_companies.json")
PRIMARY = "Kindred Capital"


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    r = requests.get(API_URL, headers=HEADERS, timeout=TIMEOUT)
    r.raise_for_status()
    rows = list(csv.DictReader(io.StringIO(r.text)))
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    for row in rows:
        name = clean(row.get("Name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(row.get("Description"))
        website = clean(row.get("Website"))
        if website and not website.startswith("http"):
            website = "https://" + website
        status_raw = (row.get("Status") or "").strip().lower()
        status = "active"
        if status_raw in ("acquired", "exited", "exit"):
            status = "acquired"
        elif status_raw in ("failed", "dead", "closed"):
            status = "active"  # don't invent; leave active unless clearly acquired
        sector = clean(row.get("Sector"))
        sectors = [s.strip() for s in sector.split(",")] if sector else None
        location = clean(row.get("Company HQ"))
        invested = clean(row.get("Investment Date"))
        # Investment Date is a calendar date, not a funding-round label
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": None,
            "location": location,
            "sectors": sectors,
            "invested_date": invested.split("T")[0] if invested else None,
            "everywhere_tags": classify(name, desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  location: {sum(1 for r in out if r.get('location'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
