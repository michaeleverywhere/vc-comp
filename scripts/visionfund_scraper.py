#!/usr/bin/env python3
"""SoftBank Vision Fund portfolio scraper -> visionfund_companies.json
Source: https://visionfund.com/portfolio — Next.js __NEXT_DATA__ holds every
PortfolioCompanies entry: name, overview (description), city/state/country,
fund (SVF1/SVF2/LatAm...), status (Public/Private/Exited...), status note
(e.g. ticker), sector, region and leadership.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, html_text
from _d50_common import rec, finish

SOURCE_URL = "https://visionfund.com/portfolio"
PRIMARY = "SoftBank Vision Fund"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "health tech": ["Health"], "healthtech": ["Health"], "consumer": ["Consumer"],
              "logistics": ["Logistics / Supply Chain"], "transportation": ["Transportation / Mobility"],
              "proptech": ["PropTech"], "real estate": ["PropTech"], "frontier tech": ["Deeptech / Robotics / AR/VR"],
              "edtech": ["Future of Work"]}


def title(o, k):
    v = o.get(k)
    return v.get("title") if isinstance(v, dict) else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch_response(SOURCE_URL).content.decode("utf-8")  # server omits charset
    data = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S).group(1))
    found = {}

    def walk(o):
        if isinstance(o, dict):
            if o.get("__typename") == "Entry_PortfolioCompanies_PortfolioCompanies" and o.get("title"):
                found.setdefault(o["id"], o)
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(data)
    out = []
    for o in found.values():
        status = title(o, "company_status")
        loc = ", ".join(x for x in (o.get("city"), o.get("state"), o.get("country")) if x) or None
        sec = title(o, "sector")
        out.append(rec(o["title"], html_text(o.get("overview") or o.get("home_overview") or "") or None, None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else None, sector_map=SECTOR_MAP,
                       location=loc, region=title(o, "region"), fund=title(o, "fund"),
                       portfolio_status=status, status_note=o.get("status_override") or None,
                       status={"public": "ipo", "exited": "exited", "private": "active"}.get((status or "").lower(), (status or "").lower() or None),
                       leadership=o.get("leadership") or None,
                       detail_url=f"https://visionfund.com/portfolio/{o['slug']}" if o.get("slug") else None))
    finish(out, "visionfund", ("description", "location", "fund", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
