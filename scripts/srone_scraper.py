#!/usr/bin/env python3
"""SR One portfolio scraper -> srone_companies.json
Source: https://www.srone.com/portfolio — Next.js (Craft CMS) __NEXT_DATA__:
entries (name, one-line focus, status) with category ids resolved via the page's
category lists: therapeutic area, ownership (private/public), phase, status.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response
from _d50_common import rec, finish

ORIGIN = "https://www.srone.com"
SOURCE_URL = ORIGIN + "/portfolio"
PRIMARY = "SR One"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch_response(SOURCE_URL).content.decode("utf-8")
    pp = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S).group(1))["props"]["pageProps"]
    cats = {g: {c["value"]: c["label"] for c in items} for g, items in (pp.get("categories") or {}).items()}
    out = []
    for e in pp.get("entries") or []:
        lab = lambda g: [cats.get(g, {}).get(x.get("id")) for x in e.get(g) or [] if cats.get(g, {}).get(x.get("id"))]
        status = (lab("status") or [None])[0] or ((e.get("companyStatus") or [{}])[0].get("slug") or "").title() or None
        own = (lab("ownership") or [None])[0]
        st = (status or "").lower()
        out.append(rec(e["title"], e.get("quote") or None, None, PRIMARY, SOURCE_URL, scraped_at,
                       therapeutic_area=", ".join(lab("area")) or None, phase=(lab("phase") or [None])[0],
                       ownership=own, portfolio_status=status,
                       status="exited" if st == "exited" else ("ipo" if own == "Public" else ("active" if st == "active" else st or None)),
                       detail_url=f"{ORIGIN}/{e['uri']}" if e.get("uri") else None))
    finish(out, "srone", ("description", "status", "therapeutic_area", "everywhere_tags"))


if __name__ == "__main__":
    main()
