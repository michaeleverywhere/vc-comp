#!/usr/bin/env python3
"""Obvious Ventures portfolio scraper -> obviousventures_companies.json
Source: https://obvious.com/portfolio/ — WordPress. The page server-renders the
first 30 companies; the rest come from the site's own "Load More" endpoint
(admin-ajax action portfolio_load_more, paged=N), which returns the same card
HTML. Each card: name, description, company website, Founded year, Pillar
(Planetary / Human / Economic Health) and, for some, a Status (e.g. Acquired,
IPO).
"""
import json, os, sys, time
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, tags_for, year_of, HEADERS, TIMEOUT

SOURCE_URL = "https://obvious.com/portfolio/"
AJAX = "https://obvious.com/wp-admin/admin-ajax.php"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "obviousventures_companies.json")
PRIMARY = "Obvious Ventures"
SECTOR_TAG_MAP = {"planetary health": ["Climate / Sustainability"], "human health": ["Health"]}


def cards(html):
    return BeautifulSoup(html or "", "html.parser").select(".list-secondary__item")


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    items = cards(fetch(SOURCE_URL))
    page = 2
    while page < 20:
        r = requests.post(AJAX, data={"action": "portfolio_load_more", "paged": page}, headers=HEADERS, timeout=TIMEOUT)
        r.raise_for_status()
        data = (r.json() or {}).get("data") or {}
        new = cards(data.get("articles"))
        if not new:
            break
        items += new
        if "data-page" not in (data.get("load_more") or ""):
            break
        page += 1
        time.sleep(0.5)
    scraped_at = datetime.now(timezone.utc).isoformat()
    out, seen = [], set()
    for it in items:
        t = it.select_one(".list-secondary__title")
        name = clean(t.get_text(" ")) if t else None
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        body = it.select_one(".list-secondary__text")
        desc = clean(body.get_text(" ")) if body else None
        meta = {}
        for m in it.select(".list-secondary__meta > div"):
            sp, st = m.select_one("span"), m.select_one("strong")
            if sp and st:
                meta[clean(sp.get_text()).rstrip(":").lower()] = clean(st.get_text(" "))
        a = it.select_one("a.list-secondary__link[href]")
        site_status = meta.get("status")
        sl = (site_status or "").lower()
        status = "acquired" if "acqui" in sl else ("active" if sl == "active" else None)
        pillar = meta.get("pillar")
        sectors = [pillar] if pillar else []
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": a["href"].strip() if a else None,
            "status": status,
            "site_status": site_status,
            "founded_year": year_of(meta.get("founded")),
            "pillar": pillar,
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
    for k in ("description", "company_url", "status", "site_status", "founded_year", "pillar", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
