#!/usr/bin/env python3
"""Resolute Ventures portfolio scraper -> resoluteventures_companies.json
Source: Prismic API resolute.cdn.prismic.io (document type company).
"""
import json, os, sys, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

API = "https://resolute.cdn.prismic.io/api/v2"
SOURCE_URL = "https://resolute.vc/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "resoluteventures_companies.json")
PRIMARY = "Resolute Ventures"


def prismic_all():
    meta = json.loads(urllib.request.urlopen(API, timeout=30).read())
    ref = meta["refs"][0]["ref"]
    q = urllib.parse.quote('[[at(document.type,"company")]]')
    page, rows = 1, []
    while True:
        url = f"{API}/documents/search?ref={ref}&q={q}&pageSize=100&page={page}"
        res = json.loads(urllib.request.urlopen(url, timeout=45).read())
        rows.extend(res.get("results") or [])
        if page >= int(res.get("total_pages") or 1):
            break
        page += 1
    return rows


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    docs = prismic_all()
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for doc in docs:
        data = doc.get("data") or {}
        name = clean(data.get("company_name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        website = None
        link = data.get("company_website")
        if isinstance(link, dict):
            website = clean(link.get("url"))
        sectors = []
        for s in data.get("sectors") or []:
            if isinstance(s, dict) and s.get("sector"):
                sectors.append(clean(s["sector"]))
        locations = []
        for loc in data.get("locations") or []:
            if isinstance(loc, dict) and loc.get("location"):
                locations.append(clean(loc["location"]))
        founders = []
        for f in data.get("founders") or []:
            if not isinstance(f, dict):
                continue
            fn = clean(f.get("name"))
            if fn:
                founders.append(fn)  # names only; no LinkedIn URLs
        logo = None
        img = data.get("company_image")
        if isinstance(img, dict):
            logo = img.get("url")
        uid = doc.get("uid")
        profile = f"https://resolute.vc/companies/{uid}" if uid else SOURCE_URL
        rec = {
            "company_name": name,
            "description": None,
            "company_url": website,
            "logo_url": logo,
            "status": "Active",
            "stage": None,
            "location": ", ".join(locations) if locations else None,
            "founders": founders or None,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, None, sectors)[:4],
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
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  founders: {sum(1 for r in out if r.get('founders'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print(f"  status: {Counter(r['status'] for r in out)}")


if __name__ == "__main__":
    main()
