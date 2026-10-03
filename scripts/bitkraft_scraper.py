#!/usr/bin/env python3
"""BITKRAFT Ventures portfolio scraper -> bitkraft_companies.json
Source: https://bitkraft.vc/portfolio/ — __NEXT_DATA__ pageProps.companies
"""
import json, os, sys, re
from collections import Counter
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://bitkraft.vc/portfolio/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "bitkraft_companies.json")
PRIMARY = "BITKRAFT"


def normalize_stage(raw):
    if not raw:
        return None
    s = str(raw).strip()
    # JSON-encoded list like '["Seed","Series A"]' — take latest-ish last entry
    if s.startswith("["):
        try:
            arr = json.loads(s)
            if isinstance(arr, list) and arr:
                s = str(arr[-1])
        except Exception:
            pass
    s = re.sub(r"^\d+\s*-\s*", "", s).strip()
    mapping = {
        "pre-seed": "Pre-Seed",
        "pre seed": "Pre-Seed",
        "seed": "Seed",
        "pre-series a": "Pre-Seed",
        "series a": "Series A",
        "series b": "Series B",
        "series c": "Series C",
        "series c+": "Series C+",
        "growth": "Growth",
        "late stage": "Late Stage",
        "n/a": None,
    }
    key = s.lower()
    if key in mapping:
        return mapping[key]
    if key.startswith("series "):
        return s.title().replace("Series C+", "Series C+")
    return clean(s) if s and s.lower() not in ("active", "n/a") else None


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        raise SystemExit("FATAL: no __NEXT_DATA__ on BITKRAFT portfolio page")
    nd = json.loads(m.group(1))
    companies = (nd.get("props") or {}).get("pageProps", {}).get("companies") or []
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for c in companies:
        name = clean(c.get("name"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        desc = clean(c.get("description") or c.get("title"))
        cat = clean(c.get("category"))
        sectors = [cat] if cat and cat.upper() != "N/A" else None
        location = clean(c.get("location"))
        stage = normalize_stage(c.get("investmentState"))
        status_raw = clean(c.get("stage"))  # site uses 'stage' for Active/etc
        status = "Active"
        if status_raw and status_raw.lower() in ("acquired", "exited", "exit"):
            status = "Acquired"
        elif status_raw and status_raw.lower() in ("public", "ipo"):
            status = "Public"
        slug = c.get("slug")
        profile = f"https://bitkraft.vc/portfolio/{slug}" if slug else SOURCE_URL
        logo = None
        if isinstance(c.get("logo"), dict) and c["logo"].get("url"):
            logo = "https://bitkraft.vc" + c["logo"]["url"] if c["logo"]["url"].startswith("/") else c["logo"]["url"]
        rec = {
            "company_name": name,
            "description": desc,
            "company_url": None,  # not in NEXT payload
            "logo_url": logo,
            "status": status,
            "stage": stage,
            "location": location,
            "sectors": sectors,
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
    print(f"  stage: {sum(1 for r in out if r.get('stage'))}/{n}")
    print(f"  location: {sum(1 for r in out if r.get('location'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
