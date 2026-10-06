#!/usr/bin/env python3
"""Headline portfolio scraper -> headline_companies.json
Source: https://headline.com/portfolio — Gatsby + Sanity. The listing's
page-data.json carries every published company (name, slug, location,
founders, fund, region, sector); each /page-data/portfolio/<slug>/page-data.json
adds Headline's statement (description), investment phases with years
(e.g. Early 2023, Growth 2026), outcome, and the page's structuredData block
(company url, founding date, employee range, ticker). Headline's phase labels
(Early/Growth) are not funding rounds, so `stage` stays null; the earliest
phase year is first_invested. team_size is Headline's published employeeRange.
"""
import json, os, re, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, year_of, HEADERS, TIMEOUT

import requests
from concurrent.futures import ThreadPoolExecutor

BASE = "https://headline.com"
SOURCE_URL = BASE + "/portfolio"
LIST_JSON = BASE + "/page-data/portfolio/page-data.json"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "headline_companies.json")
PRIMARY = "Headline"
SECTOR_TAG_MAP = {"fintech": ["FinTech / Insurance"], "consumer": ["Consumer"], "healthcare": ["Health"],
                  "infrastructure": ["Dev Tools / Cloud"]}


def page_json(slug):
    url = f"{BASE}/page-data/portfolio/{slug}/page-data.json"
    for _ in range(3):
        try:
            r = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            if r.status_code == 404:
                return slug, None
            r.raise_for_status()
            return slug, ((r.json().get("result") or {}).get("data") or {}).get("page")
        except (requests.RequestException, ValueError):
            pass
    return slug, None


def statement(blocks):
    parts = []
    for b in blocks or []:
        t = "".join(c.get("text") or "" for c in b.get("children") or [])
        if clean(t):
            parts.append(clean(t))
    return " ".join(parts) or None


def titles(lst, key):
    return [clean(((x or {}).get(key) or {}).get("title")) for x in lst or [] if ((x or {}).get(key) or {}).get("title")]


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    data = fetch(LIST_JSON, as_json=True)["result"]["data"]
    nodes = [n for n in data["companies"]["nodes"] if not n.get("hidden") and (n.get("slug") or {}).get("current")]
    if limit:
        nodes = nodes[:limit]
    with ThreadPoolExecutor(max_workers=4) as ex:
        pages = dict(ex.map(page_json, [n["slug"]["current"] for n in nodes]))
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for n in nodes:
        slug = n["slug"]["current"]
        p = pages.get(slug) or {}
        name = clean(p.get("title") or n.get("title"))
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        sd = p.get("structuredData") or {}
        stages = p.get("stages") or []
        years = [year_of(s.get("year")) for s in stages if year_of(s.get("year"))]
        outcome = p.get("outcome") or []
        out_txt = ", ".join(clean(" ".join(str(o.get(k) or "") for k in ("phase", "year"))) or "" for o in outcome
                            if isinstance(o, dict) and o.get("phase")) or None
        desc = statement(p.get("_rawStatement")) or clean(p.get("subline")) or clean((p.get("seo") or {}).get("description"))
        sectors = titles(p.get("sectors") or n.get("sectors"), "sector")
        ol = (out_txt or "").lower()
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": clean(sd.get("url")),
            "company_profile_url": f"{SOURCE_URL}/{slug}/",
            "status": "acquired" if re.search(r"acqui|aquired|\baqu\.|m&a", ol) else None,
            "outcome": out_txt,
            "stage": None,
            "investment_phases": [{"phase": s.get("phase"), "year": s.get("year")} for s in stages],
            "first_invested": min(years) if years else None,
            "founded_date": clean(sd.get("foundingDate")),
            "location": clean(p.get("location") or n.get("location")),
            "founders": [clean(f) for f in (p.get("founders") or n.get("founders") or []) if clean(f)],
            "team_size": clean(sd.get("employeeRange")),
            "ticker_symbol": clean(sd.get("tickerSymbol")),
            "fund": titles(n.get("fund"), "fund"),
            "regions": titles(n.get("regions"), "region"),
            "sectors": sectors,
            "everywhere_tags": tags_for(name, desc, sectors, SECTOR_TAG_MAP),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "outcome", "first_invested", "location", "founders", "team_size", "sectors", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
