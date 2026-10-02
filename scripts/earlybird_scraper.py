#!/usr/bin/env python3
"""Earlybird portfolio scraper -> earlybird_companies.json
Source: https://earlybird.com/companies/ — Framer SSR cards with name/status/stage/city/sector.
"""
import json, os, re, sys
from collections import Counter
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "automation"))
from tags import classify

SOURCE_URL = "https://earlybird.com/companies/"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "earlybird_companies.json")
PRIMARY = "Earlybird"

STATUS_MAP = {
    "active": "Active",
    "exit": "Exited",
    "exited": "Exited",
    "acquired": "Acquired",
    "ipo": "Public",
    "written off": "Inactive",
    "inactive": "Inactive",
}

# Funding-round-like stages only
ROUND_OK = re.compile(
    r"^(pre-?seed|seed|series\s*[a-h]|growth|series\s*a|series\s*b|series\s*c)$",
    re.I,
)


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    html = fetch(SOURCE_URL)
    soup = BeautifulSoup(html, "html.parser")
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for a in soup.select('a[href*="/companies/"]'):
        href = a.get("href") or ""
        if href.rstrip("/").endswith("companies"):
            continue
        parts = [clean(t) for t in a.stripped_strings if clean(t)]
        if len(parts) < 2:
            continue
        name = parts[0]
        if not name or name.lower() in seen:
            continue
        if name.lower() in ("portfolio", "about", "earlybird", "jobs"):
            continue
        seen.add(name.lower())
        status_raw = parts[1] if len(parts) > 1 else None
        stage_raw = parts[2] if len(parts) > 2 else None
        city = parts[3] if len(parts) > 3 else None
        sector = parts[4] if len(parts) > 4 else None
        status = STATUS_MAP.get((status_raw or "").lower(), "Active")
        stage = None
        if stage_raw and ROUND_OK.match(stage_raw.strip()):
            stage = clean(stage_raw)
        profile = href if href.startswith("http") else urljoin(SOURCE_URL, href)
        sectors = [sector] if sector else []
        rec = {
            "company_name": name,
            "description": None,  # list page has no blurb; sector used for tags
            "company_url": None,
            "status": status,
            "stage": stage,
            "location": city,
            "sectors": sectors,
            "everywhere_tags": classify(name, sector, sectors)[:4],
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
    print(f"  status: {Counter(r['status'] for r in out)}")
    print(f"  stage: {sum(1 for r in out if r.get('stage'))}/{n}")
    print(f"  everywhere_tags: {sum(1 for r in out if r['everywhere_tags'])}/{n}")
    print("  caveat: list-page only (name/status/stage/city/sector); no descriptions")


if __name__ == "__main__":
    main()
