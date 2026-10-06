#!/usr/bin/env python3
"""Partech portfolio scraper -> partech_companies.json
Source: https://partechpartners.com/companies — Next.js; the page's
__NEXT_DATA__ carries the full company list (name, short text, description,
website, HQ country, region, Partech fund(s), sectors, status Current/Alumni).
"Current" maps to lead status active (the site's own label); Alumni stays as
site_status only. The fund names (Seed / Venture / Growth / Africa / Impact)
are Partech funds, not funding rounds, so `stage` is left empty.
"""
import json, os, re, sys
from datetime import datetime, timezone
from urllib.parse import urljoin

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for

BASE = "https://partechpartners.com"
SOURCE_URL = BASE + "/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "partech_companies.json")
PRIMARY = "Partech"
SECTOR_TAG_MAP = {
    "financial services": ["FinTech / Insurance"], "healthcare": ["Health"], "climate": ["Climate / Sustainability"],
    "consumer": ["Consumer"], "food & agritech": ["CPG", "Climate / Sustainability"],
    "industrial, energy & iot": ["Deeptech / Robotics / AR/VR"], "infrastructure saas": ["Dev Tools / Cloud"],
}


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("FATAL: __NEXT_DATA__ not found")
    comps = json.loads(m.group(1))["props"]["pageProps"]["companies"]
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for c in comps:
        name = clean(c.get("name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        st = clean(((c.get("status") or {}).get("status")))
        sectors = [clean(s.get("sector")) for s in c.get("sectors") or [] if clean(s.get("sector"))]
        desc = clean(c.get("description")) or clean(c.get("short_text"))
        hq = [clean(h.get("location")) for h in c.get("hq_locations") or [] if clean(h.get("location"))]
        out.append({
            "company_name": name,
            "description": desc,
            "tagline": clean(c.get("short_text")),
            "company_url": clean(c.get("external_link")),
            "company_profile_url": urljoin(BASE, c["internal_link"]) if c.get("internal_link") else None,
            "status": "active" if (st or "").lower() == "current" else None,
            "site_status": st,
            "location": ", ".join(hq) or None,
            "regions": [clean(l.get("location")) for l in c.get("locations") or [] if clean(l.get("location"))],
            "investment_funds": [clean(f.get("investment_fund")) for f in c.get("investment_funds") or [] if clean(f.get("investment_fund"))],
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
        if limit and len(out) >= limit:
            break
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "site_status", "location", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
