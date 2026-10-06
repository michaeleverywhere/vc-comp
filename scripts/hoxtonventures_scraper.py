#!/usr/bin/env python3
"""Hoxton Ventures portfolio scraper -> hoxtonventures_companies.json
Source: https://hoxtonventures.com/portfolio/ — WordPress + FacetWP (server
rendered). The grid gives every company (logo alt = name) and an outcome badge
(Acquired / IPO / Shut down / Administration ...); the `?_statuses=active`
facet view lists the companies the site marks Active. Each /portfolio/<slug>/
detail page adds description, website, founders, Founded In, Fund,
Headquarters, Invested In and the Hoxton partner.
"""
import json, os, re, sys
from datetime import datetime, timezone

from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean, tags_for, year_of, is_social

SOURCE_URL = "https://hoxtonventures.com/portfolio/"
ACTIVE_URL = SOURCE_URL + "?_statuses=active"
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "hoxtonventures_companies.json")
PRIMARY = "Hoxton Ventures"


def grid(html):
    s = BeautifulSoup(html, "html.parser")
    out = []
    for a in s.select("a.loop-portfolio[href]"):
        img = a.select_one("img.loop-portfolio__logo")
        b = a.select_one(".loop-portfolio__badge")
        out.append({"profile": a["href"].strip(), "name": clean(img.get("alt")) if img else None,
                    "badge": clean(b.get_text()) if b else None})
    return out


def main():
    limit = int(sys.argv[sys.argv.index("--limit") + 1]) if "--limit" in sys.argv else None
    rows = grid(fetch(SOURCE_URL))
    active = {r["profile"] for r in grid(fetch(ACTIVE_URL))}
    seen, uniq = set(), []
    for r in rows:
        if r["profile"] not in seen:
            seen.add(r["profile"])
            uniq.append(r)
    rows = uniq[:limit] if limit else uniq
    pages = fetch_many([r["profile"] for r in rows])
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    for r in rows:
        d = BeautifulSoup(pages.get(r["profile"]) or "", "html.parser")
        h1 = d.select_one(".content-portfolio__heading")
        name = clean(h1.get_text()) if h1 else r["name"]
        if not name:
            continue
        copy = d.select_one(".content-portfolio__copy")
        paras, site = [], None
        if copy:
            for p in copy.select("p"):
                a = p.select_one("a[href]")
                t = clean(p.get_text(" "))
                if a and t and len(t) < 60 and not is_social(a["href"]):
                    site = site or a["href"].strip()
                elif t:
                    paras.append(t)
        meta = {}
        for m in d.select(".content-portfolio__meta"):
            lab = m.select_one(".text-label")
            if not lab:
                continue
            key = clean(lab.get_text()).lower()
            if key == "founders":
                meta[key] = [clean(x.get_text()) for x in m.select("a, p:not(.text-label)") if clean(x.get_text())]
            else:
                vals = [clean(x.get_text(" ")) for x in m.find_all("p") if x is not lab and clean(x.get_text())]
                meta[key] = ", ".join(vals) if vals else None
        badge = r["badge"]
        bl = (badge or "").lower()
        if r["profile"] in active:
            status = "active"
        elif "acqui" in bl:
            status = "acquired"
        else:
            status = None
        tick = re.match(r"(NYSE|NASDAQ)\s*:\s*([A-Z.]+)", badge or "", re.I)
        desc = " ".join(paras) or None
        out.append({
            "company_name": name,
            "description": desc,
            "company_url": site,
            "company_profile_url": r["profile"],
            "status": status,
            "site_status": "Active" if r["profile"] in active else badge,
            "ticker": f"{tick.group(1).upper()}: {tick.group(2)}" if tick else None,
            "first_invested": year_of(meta.get("invested in")),
            "founded_year": year_of(meta.get("founded in")),
            "location": meta.get("headquarters"),
            "fund": meta.get("fund"),
            "founders": meta.get("founders") or [],
            "hoxton_partners": [clean(x) for x in (meta.get("hoxton partners") or "").split(",") if clean(x)],
            "everywhere_tags": tags_for(name, desc, []),
            "primary_investor": PRIMARY,
            "source_url": SOURCE_URL,
            "scraped_at": scraped_at,
        })
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=2)
    n = len(out)
    print(f"wrote {n} companies -> {OUT}")
    for k in ("description", "company_url", "status", "site_status", "first_invested", "founded_year", "location", "founders", "everywhere_tags"):
        print(f"  {k}: {sum(1 for x in out if x.get(k))}/{n}")


if __name__ == "__main__":
    main()
