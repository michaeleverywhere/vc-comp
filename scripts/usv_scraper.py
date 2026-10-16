#!/usr/bin/env python3
"""Union Square Ventures portfolio scraper -> usv_companies.json
Source: https://www.usv.com/portfolio — Next.js App Router page; the RSC flight
payload embeds every company record: name, description, website, entry round,
investment year, current stage (early/growth/public/acquired/inactive) and status note.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch
from _d50_common import rec, finish

SOURCE_URL = "https://www.usv.com/portfolio"
PRIMARY = "Union Square Ventures"
STATUS = {"early": "active", "growth": "active", "public": "ipo", "acquired": "acquired", "inactive": "inactive"}


def records(html):
    chunks = re.findall(r'self\.__next_f\.push\(\[1,"(.*?)"\]\)</script>', html, re.S)
    flight = "".join(json.loads('"' + c + '"') for c in chunks)
    dec, objs = json.JSONDecoder(), {}
    for m in re.finditer(r'\{"_id":"company-', flight):
        try:
            o, _ = dec.raw_decode(flight, m.start())
        except ValueError:
            continue
        if o.get("name"):
            objs.setdefault(o["_id"], o)
    return list(objs.values())


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for o in records(fetch(SOURCE_URL)):
        stage = (o.get("currentStage") or "").lower()
        out.append(rec(o["name"], o.get("description"), o.get("website"), PRIMARY, SOURCE_URL, scraped_at,
                       entry_round=o.get("investmentRound") or None, first_invested_year=o.get("investmentYear"),
                       current_stage=stage or None, status=STATUS.get(stage, stage or None),
                       status_note=o.get("statusNote") or None, token_ticker=o.get("tokenTicker") or None,
                       detail_url=f"https://www.usv.com/portfolio/company/{o['slug']}" if o.get("slug") else None))
    finish(out, "usv", ("description", "company_url", "first_invested_year", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
