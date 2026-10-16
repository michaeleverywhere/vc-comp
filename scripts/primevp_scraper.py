#!/usr/bin/env python3
"""Prime Venture Partners portfolio scraper -> primevp_companies.json
Source: https://www.primevp.in/portfolio — Next.js __NEXT_DATA__ (Strapi
CompanyPageData): name, description, website, sectors, founders, and the
funding-round history the firm publishes (RaiseDetailItem, IsPrime = rounds
Prime took part in).
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, html_text, stage_label
from _d50_common import rec, finish

SOURCE_URL = "https://www.primevp.in/portfolio"
PRIMARY = "Prime Venture Partners"
SECTOR_MAP = {"fintech": ["FinTech / Insurance"], "ai + saas": ["Future of Work"], "consumer tech": ["Consumer"],
              "health tech": ["Health"], "healthtech": ["Health"], "edtech": ["Consumer"], "gaming": ["Gaming / Media / Entertainment"],
              "deeptech": ["Deeptech / Robotics / AR/VR"], "climate": ["Climate / Sustainability"], "education": ["Consumer"]}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    html = fetch(SOURCE_URL)
    nd = json.loads(re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S).group(1))
    out = []
    for e in nd["props"]["pageProps"]["pageData"]["CompanyPageData"]["data"]:
        a = e.get("attributes") or {}
        sectors = [((s.get("attributes") or {}).get("Title")) for s in ((a.get("Sectors") or {}).get("data") or [])]
        founders = [((f.get("attributes") or {}).get("Name")) for f in ((a.get("Founders") or {}).get("data") or [])]
        rounds = [clean(r.get("RaiseInfo")) for r in (a.get("RaiseDetailItem") or []) if clean(r.get("RaiseInfo"))]
        prime_rounds = [clean(r.get("RaiseInfo")) for r in (a.get("RaiseDetailItem") or []) if r.get("IsPrime") and clean(r.get("RaiseInfo"))]
        first = prime_rounds[0] if prime_rounds else None
        out.append(rec(a.get("Name"), html_text(a.get("ShortDescription") or a.get("CardDescription") or ""),
                       a.get("CompanyWebsite"), PRIMARY, SOURCE_URL, scraped_at, sectors=sectors, sector_map=SECTOR_MAP,
                       founders=[clean(x) for x in founders if clean(x)], funding_rounds=rounds,
                       prime_rounds=prime_rounds, first_investment_round=first,
                       stage=stage_label(first.split(" - ")[0]) if first else None))
    finish(out, "primevp", ("description", "company_url", "founders", "funding_rounds", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
