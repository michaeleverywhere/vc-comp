#!/usr/bin/env python3
"""Founderful (formerly Wingman Ventures) portfolio scraper -> founderful_companies.json
Source: https://www.founderful.com/founderful-family — Founderful, Zurich-based pre-seed/seed VC for Swiss tech
startups (formerly Wingman Ventures). The "Founderful family" page is rendered from the site's public Sanity CMS
dataset; this scraper reads the same "portfolio" documents the page uses: company name, description, website,
industries (Industrial Tech / B2B Software / Consumer Tech / Alumni), first round, year and pictured founders."""
import os, sys, json
from datetime import datetime, timezone
from urllib.parse import quote

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.founderful.com/founderful-family"
PRIMARY = "Founderful"
API = "https://oeaih8rj.apicdn.sanity.io/v2021-10-21/data/query/production?query="
QUERY = '*[_type=="portfolio"]{name,content,website,industries,round,year,"slug":slug.current,' \
        '"people":[image1.alt,image2.alt,image3.alt]}'
IND = {"industrial-tech": "Industrial Tech", "b2b-software": "B2B Software", "consumer-tech": "Consumer Tech"}


def text(blocks):
    parts = []
    for b in blocks or []:
        for c in b.get("children") or []:
            if c.get("text"):
                parts.append(c["text"])
    return clean(" ".join(parts))


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    docs = json.loads(fetch(API + quote(QUERY)))["result"]
    out = []
    for d in sorted(docs, key=lambda x: (x.get("name") or "").lower()):
        name = clean(d.get("name"))
        if not name:
            continue
        inds = d.get("industries") or []
        sectors = [IND[i] for i in inds if i in IND] or None
        people = [clean(p) for p in d.get("people") or [] if p and clean(p)]
        out.append(rec(name, text(d.get("content")), d.get("website"), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sectors, status="Alumni" if "alumni" in inds else "Active",
                       first_round=clean(d.get("round")), year=clean(d.get("year")),
                       founders=people or None,
                       profile_url=f"https://www.founderful.com/founderful-family/{d['slug']}" if d.get("slug") else None))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Founderful companies")
    finish(out, "founderful", ("description", "website", "year", "everywhere_tags"))


if __name__ == "__main__":
    main()
