#!/usr/bin/env python3
"""Abingworth portfolio scraper -> abingworth_companies.json
Source: https://www.abingworth.com/portfolio — Next.js (Craft CMS) __NEXT_DATA__:
entries (name, location) with category ids resolved via the page's categories:
status (Active/Exited), sector, strategy (Venture Capital / Clinical Co-Development /
VIPEs), region and Abingworth fund(s). No descriptions in the list payload.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

ORIGIN = "https://www.abingworth.com"
SOURCE_URL = ORIGIN + "/portfolio"
PRIMARY = "Abingworth"
SECTOR_MAP = {"therapeutics": ["BioTech"], "medtech": ["Health"], "medical devices": ["Health"], "diagnostics": ["Health"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch_response(SOURCE_URL).content.decode("utf-8")
    pp = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S).group(1))["props"]["pageProps"]
    cats = {c["id"]: clean(c["title"]) for c in pp.get("categories") or []}
    out = []
    for e in pp.get("entries") or []:
        lab = lambda g: [cats[x["id"]] for x in e.get(g) or [] if isinstance(x, dict) and x.get("id") in cats]
        status = (lab("status") or [None])[0]
        out.append(rec(e["title"], None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=lab("sector"), sector_map=SECTOR_MAP,
                       location=clean(e.get("location")) or None, region=", ".join(lab("region")) or None,
                       strategy=", ".join(lab("strategy")) or None, fund=", ".join(lab("funds")) or None,
                       portfolio_status=status, status={"active": "active", "exited": "exited"}.get((status or "").lower()),
                       detail_url=f"{ORIGIN}/{e['uri']}" if e.get("uri") else None))
    finish(out, "abingworth", ("status", "location", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
