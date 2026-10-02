#!/usr/bin/env python3
"""Costanoa Ventures portfolio scraper -> costanoa_companies.json
Source: Prismic API (costanoa repo); site https://www.costanoa.vc/portfolio.
"""
import json, os, sys, urllib.parse, urllib.request
from collections import Counter
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.costanoa.vc/portfolio"
API = "https://costanoa.cdn.prismic.io/api/v2"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "costanoa_companies.json")
PRIMARY = "Costanoa Ventures"


def prismic_all_companies():
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


def rich_text(blocks):
    if not blocks:
        return None
    parts = []
    for b in blocks:
        if isinstance(b, dict) and b.get("text"):
            parts.append(b["text"])
    return clean(" ".join(parts)) if parts else None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    docs = prismic_all_companies()
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for doc in docs:
        data = doc.get("data") or {}
        name = clean(data.get("name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        slogan = clean(data.get("slogan"))
        desc = rich_text(data.get("content")) or slogan
        link = data.get("external_link") or {}
        website = clean(link.get("url")) if isinstance(link, dict) else None
        cats = []
        for c in data.get("filter_category") or []:
            if isinstance(c, dict) and c.get("category"):
                cats.append(clean(c["category"]))
        # Featured is curation, not sector
        sectors = [c for c in cats if c and c.lower() != "featured"]
        founders = []
        for p in data.get("leadership") or []:
            if not isinstance(p, dict):
                continue
            n = clean(p.get("name"))
            pos = (p.get("position") or "").lower()
            if n and "founder" in pos:
                founders.append(n)
        logo = None
        if isinstance(data.get("logo"), dict):
            logo = data["logo"].get("url")
        slug = (doc.get("slugs") or [None])[0]
        profile = f"https://www.costanoa.vc/portfolio/{slug}" if slug else SOURCE_URL
        # Exited filter if present
        status = "Active"
        if any((c or "").lower() in ("exited", "exit", "acquired") for c in cats):
            status = "Exited"
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "logo_url": logo,
            "status": status,
            "stage": None,
            "founders": founders or None,
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
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
