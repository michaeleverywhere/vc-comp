#!/usr/bin/env python3
"""Guinness Ventures portfolio scraper -> guinnessventures_companies.json
Source: https://www.guinnessventures.com/portfolio — Guinness Ventures, London-based EIS/SEIS venture investor (part
of Guinness Global Investors) backing UK growth companies. The portfolio page is rendered from the site's public
content API (api.guinnessventures.com); this scraper reads the same published portfolio records: company name,
description, website, founders, sector tags and current/exited state."""
import os, sys, json
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.guinnessventures.com/portfolio"
PRIMARY = "Guinness Ventures"
API = "https://api.guinnessventures.com/items/portfolio?limit=-1&filter[status][_eq]=published"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    data = json.loads(fetch(API))["data"]
    out, seen = [], set()
    for d in sorted(data, key=lambda x: (x.get("name") or "").lower()):
        if d.get("status") != "published":
            continue
        name = clean(d.get("name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(BeautifulSoup(d["description"], "html.parser").get_text(" ")) if d.get("description") else None
        state = clean(d.get("state"))
        founders = clean(d.get("founders"))
        out.append(rec(name, desc, d.get("external_link"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[clean(t) for t in d.get("tags") or [] if clean(t)] or None,
                       status=state.capitalize() if state else None, founders=founders,
                       profile_url=f"https://www.guinnessventures.com/portfolio/{d['slug']}" if d.get("slug") else None))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Guinness Ventures companies")
    finish(out, "guinnessventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
