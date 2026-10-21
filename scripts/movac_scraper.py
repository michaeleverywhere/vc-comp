#!/usr/bin/env python3
"""Movac portfolio scraper -> movac_companies.json
Source: https://movac.co.nz/investment-portfolio/ — New Zealand VC; the portfolio grid is built from Movac's own
Prismic CMS (movac.cdn.prismic.io, "investment" documents, read via the public Prismic API): company name,
Movac's industry labels, stage, fund(s), founders, CEO(s), website and the "Company profile" text."""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urlencode

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://movac.co.nz/investment-portfolio/"
API = "https://movac.cdn.prismic.io/api/v2"
PRIMARY = "Movac"


def profile(about):
    """Text of the paragraphs under the 'Company profile' heading (stops at the next heading)."""
    out, on = [], False
    for b in about or []:
        if b.get("type", "").startswith("heading"):
            on = "profile" in (b.get("text") or "").lower()
            continue
        if on and b.get("type") == "paragraph" and clean(b.get("text")):
            out.append(clean(b["text"]))
    return " ".join(out) or None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    ref = next(r["ref"] for r in fetch(API, as_json=True)["refs"] if r.get("isMasterRef"))
    docs, page = [], 1
    while True:
        q = urlencode({"ref": ref, "q": '[[at(document.type,"investment")]]', "pageSize": 100, "page": page})
        j = fetch(f"{API}/documents/search?{q}", as_json=True)
        docs += j["results"]
        if page >= j.get("total_pages", 1):
            break
        page += 1
    out = []
    for d in docs:
        x = d.get("data") or {}
        name = clean(x.get("name"))
        if not name:
            continue
        inds = [clean(((i.get("industry") or {}).get("data") or {}).get("name")) for i in x.get("industry") or []]
        funds = [clean(((f.get("fund") or {}).get("data") or {}).get("name")) for f in x.get("fund") or []]
        web = (x.get("website") or {}).get("url")
        out.append(rec(name, profile(x.get("about")), web, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[i for i in inds if i], stage=clean(x.get("stage")),
                       movac_funds=[f for f in funds if f],
                       founders=[clean(p.get("name")) for p in x.get("founders") or [] if clean(p.get("name"))],
                       ceo=", ".join(clean(p.get("name")) for p in x.get("ce_os") or [] if clean(p.get("name"))) or None))
    if len(out) < 40:
        raise SystemExit(f"FATAL: only {len(out)} Movac companies")
    finish(out, "movac", ("description", "company_url", "sectors", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
