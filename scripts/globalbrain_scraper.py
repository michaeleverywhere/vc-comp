#!/usr/bin/env python3
"""Global Brain portfolio scraper -> globalbrain_companies.json
Source: https://globalbrains.com/en/portfolio — Nuxt 3 payload (__NUXT_DATA__).
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://globalbrains.com/en/portfolio"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "globalbrain_companies.json")
PRIMARY = "Global Brain"


def resolve(data, ref):
    if isinstance(ref, int) and 0 <= ref < len(data):
        return data[ref]
    return ref


def deref_obj(data, obj):
    """Resolve Nuxt payload object whose values are indices into the flat array."""
    if not isinstance(obj, dict):
        return {}
    out = {}
    for k, v in obj.items():
        val = resolve(data, v)
        # one more hop if still an int pointing at a scalar
        if isinstance(val, int) and 0 <= val < len(data) and not isinstance(data[val], (dict, list)):
            val = data[val]
        out[k] = val
    return out


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    el = soup.select_one('script[type="application/json"]')
    if not el or not el.string:
        raise SystemExit("FATAL: no Nuxt JSON payload on Global Brain portfolio page")
    data = json.loads(el.string)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()

    for item in data:
        if not isinstance(item, dict):
            continue
        if "nameEn" not in item and "nameJa" not in item:
            continue
        if "websiteEn" not in item and "websiteJa" not in item:
            continue
        rec_raw = deref_obj(data, item)
        name = clean(rec_raw.get("nameEn") or rec_raw.get("nameJa"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        website = clean(rec_raw.get("websiteEn") or rec_raw.get("websiteJa"))
        status_raw = (rec_raw.get("status") or "").lower() if isinstance(rec_raw.get("status"), str) else ""
        status = "active"
        if status_raw in ("exit", "exited", "acquired", "ipo", "public"):
            status = "acquired" if status_raw != "ipo" and status_raw != "public" else "active"
            if status_raw in ("ipo", "public"):
                status = "active"  # keep active; IPO not in our lead-status enum of acquired
        sector = clean(rec_raw.get("sector")) if isinstance(rec_raw.get("sector"), str) else None
        region = clean(rec_raw.get("region")) if isinstance(rec_raw.get("region"), str) else None
        invested = rec_raw.get("investedAt")
        invested_s = None
        if isinstance(invested, str) and invested.strip():
            # keep date string as first_invested only if it looks like a funding round — it doesn't
            invested_s = clean(invested.split(" ")[0])  # YYYY-MM-DD portion
        sectors = [sector] if sector else None
        # region as location if present (slug like north-america)
        location = None
        if region:
            location = region.replace("-", " ").title()

        rec = {
            "company_name": name,
            "description": None,  # not in payload
            "company_url": website,
            "status": "acquired" if status_raw in ("exit", "exited", "acquired") else "active",
            "stage": None,
            "location": location,
            "sectors": sectors,
            "invested_date": invested_s,
            "everywhere_tags": classify(name, None, sectors)[:4],
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
    print(f"  company_url: {sum(1 for r in out if r.get('company_url'))}/{n}")
    print(f"  location: {sum(1 for r in out if r.get('location'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")


if __name__ == "__main__":
    main()
