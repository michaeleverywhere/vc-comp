#!/usr/bin/env python3
"""Project A portfolio scraper -> projecta_companies.json
Source: Sanity API project nykgtoh6 (site https://www.project-a.vc/companies).
"""
import json, os, sys, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.project-a.vc/companies"
API = "https://nykgtoh6.api.sanity.io/v2021-10-21/data/query/production"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "projecta_companies.json")
PRIMARY = "Project A"

STATUS_MAP = {
    "active": "Active",
    "exited": "Exited",
    "acquired": "Acquired",
    "ipo": "Public",
    "inactive": "Inactive",
}


def sanity_query(q: str):
    url = f"{API}?query={urllib.parse.quote(q)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())["result"]


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    rows = sanity_query(
        '*[_type=="portfolioCompany"]{title, "slug": slug.current, website, description, status, founded, foundingTeam, industries, ventureThemes, investedAt, projectInvestedAt}'
    )
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for row in rows:
        name = clean(row.get("title") or (row.get("slug") or "").replace("-", " ").title())
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(row.get("description"))
        website = clean(row.get("website"))
        status = STATUS_MAP.get((row.get("status") or "").lower(), "Active" if row.get("status") else "Active")
        industries = row.get("industries") or []
        themes = row.get("ventureThemes") or []
        if isinstance(industries, str):
            industries = [industries]
        if isinstance(themes, str):
            themes = [themes]
        sectors = [clean(x) for x in list(industries) + list(themes) if clean(x)]
        founders = row.get("foundingTeam") or None
        if isinstance(founders, list):
            founders = [clean(x) if isinstance(x, str) else clean(x.get("name")) for x in founders]
            founders = [f for f in founders if f] or None
        year = None
        for key in ("investedAt", "projectInvestedAt", "founded"):
            v = row.get(key)
            if isinstance(v, int) and 1980 <= v <= 2030:
                if key == "founded":
                    pass
                else:
                    year = v
                    break
            if isinstance(v, str) and len(v) >= 4 and v[:4].isdigit():
                year = int(v[:4])
                break
        founded = row.get("founded") if isinstance(row.get("founded"), int) else None
        profile = f"https://www.project-a.vc/companies/{row.get('slug')}" if row.get("slug") else SOURCE_URL
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": None,
            "founded_year": founded,
            "investment_year": year,
            "founders": founders,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": profile,
            "scraped_at": scraped_at,
        }
        out.append(rec)
        if limit and len(out) >= limit:
            break

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    print(f"  description: {sum(1 for r in out if r.get('description'))}/{n}")
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
