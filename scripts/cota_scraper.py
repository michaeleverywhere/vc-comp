#!/usr/bin/env python3
"""Cota Capital portfolio scraper -> cota_companies.json
Source: https://www.cotacapital.com/companies/ — the page embeds its full company
list as a `var data_companies = [...]` JSON array (name, description, HQ,
website, founders, acquired flag).
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, html_text, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.cotacapital.com/companies/"
PRIMARY = "Cota Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    m = re.search(r"var data_companies = (\[.*?\]);\s*\n", html, re.S)
    data = json.loads(m.group(1))
    out = []
    for c in data:
        acq = clean(html_text(c.get("acquired") or "") if isinstance(c.get("acquired"), str) else None)
        founders = [clean(x.get("text")) for x in (c.get("leadership") or []) if isinstance(x, dict) and clean(x.get("text"))]
        site = (c.get("website") or {}).get("url") if isinstance(c.get("website"), dict) else None
        out.append(rec(html_text(c.get("post_title")), html_text(c.get("description") or ""), site, PRIMARY, SOURCE_URL,
                       scraped_at, location=c.get("hq"), founders=founders,
                       status=("ipo" if acq and "ipo" in acq.lower() else "acquired") if acq else "active", exit_note=acq))
    finish(out, "cota", ("description", "company_url", "location", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
