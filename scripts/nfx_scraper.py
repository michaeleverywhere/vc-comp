#!/usr/bin/env python3
"""NFX portfolio scraper -> nfx_companies.json
Source: https://www.nfx.com/companies — Next.js __NEXT_DATA__ WordPress companies.
"""
import json, os, re, sys
from datetime import datetime, timezone
from html import unescape

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://www.nfx.com/companies"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "nfx_companies.json")
PRIMARY = "NFX"

STAGE_MAP = {
    "pre-seed": "Pre-Seed",
    "preseed": "Pre-Seed",
    "seed": "Seed",
    "series a": "Series A",
    "series b": "Series B",
    "series c": "Series C",
    "series d": "Series D",
    "series e": "Series E",
    "growth": "Growth",
}


def norm_stage(s):
    if not s:
        return None
    key = s.strip().lower()
    return STAGE_MAP.get(key, s.strip() if re.search(r"(?i)seed|series|pre-?seed|growth", s) else None)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    nd = soup.select_one("#__NEXT_DATA__")
    if not nd or not nd.string:
        raise SystemExit("FATAL: no __NEXT_DATA__ on NFX companies page")
    payload = json.loads(nd.string)
    companies = payload["props"]["pageProps"]["companies"]
    cats = {c["id"]: c.get("name") for c in (payload["props"]["pageProps"].get("focusAreaCategories") or [])}
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    for c in companies:
        title = c.get("title")
        if isinstance(title, dict):
            title = title.get("rendered")
        name = clean(unescape(title or ""))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        acf = c.get("acf") or {}
        desc = clean(acf.get("content") or acf.get("sub_text"))
        website = clean(acf.get("link"))
        stage = norm_stage(clean(acf.get("first_partnered")))
        status_raw = (acf.get("status") or "").strip().lower()
        status = "active"
        if status_raw in ("acquired", "exited", "exit"):
            status = "acquired"
        elif status_raw in ("active", "public", "ipo", ""):
            status = "active"
        focus_ids = acf.get("focus_area_category_ids") or []
        sectors = []
        for fid in focus_ids:
            n = cats.get(fid) or cats.get(str(fid))
            if n and n not in sectors:
                sectors.append(n)
        # also from focusAreas if present
        for fa in c.get("focusAreas") or []:
            if isinstance(fa, dict) and fa.get("name") and fa["name"] not in sectors:
                sectors.append(fa["name"])
            elif isinstance(fa, str) and fa not in sectors:
                sectors.append(fa)

        rec = {
            "company_name": name,
            "description": desc,
            "company_url": website,
            "status": status,
            "stage": stage,
            "sectors": sectors or None,
            "everywhere_tags": classify(name, desc, sectors)[:4],
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
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
    print(f"  stage: {sum(1 for r in out if r.get('stage'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
