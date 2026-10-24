#!/usr/bin/env python3
"""Draper Triangle Ventures portfolio scraper -> drapertriangle_companies.json
Source: https://drapertriangle.com/portfolio/ — Draper Triangle Ventures, Pittsburgh/Columbus/Ann Arbor early-stage
venture capital firm (Draper Venture Network member) backing Midwest entrepreneurs. The portfolio page lists current
portfolio companies and select exits; each company profile page gives the name, summary, longer description and
company website."""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean
from _d50_common import rec, finish

SOURCE_URL = "https://drapertriangle.com/portfolio/"
PRIMARY = "Draper Triangle Ventures"
SKIP = re.compile(r"drapertriangle|drapernetwork|facebook|linkedin|twitter|youtube|gmpg|browsehappy|wp\.com", re.I)


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    items, status = [], "Active"
    for el in soup.select("h3, ul.portfolio-list a[href], ul.selects-list a[href]"):
        if el.name == "h3":
            t = clean(el.get_text(" ")) or ""
            status = "Exited" if "exit" in t.lower() else "Active" if "current" in t.lower() else status
            continue
        u = el["href"].replace("http://", "https://")
        if "/portfolio/" in u and u.rstrip("/") != SOURCE_URL.rstrip("/") and u not in [i[0] for i in items]:
            img = el.find("img")
            items.append((u, status, clean(img.get("alt")) if img else None))
    pages = fetch_many([u for u, _, _ in items])
    out, seen = [], set()
    for u, st, alt in items:
        html = pages.get(u)
        if not html:
            continue
        s = BeautifulSoup(html, "html.parser")
        box = s.select_one(".memberText") or s
        h1 = box.find("h1")
        name = clean(h1.get_text(" ")) if h1 else alt
        if not name or name.lower() in seen:
            continue
        seen.add(name.lower())
        h6 = box.find("h6")
        ps = [clean(p.get_text(" ")) for p in box.select(".entry-content > p")]
        ps = [p for p in ps if p]
        desc = clean(h6.get_text(" ")) if h6 and clean(h6.get_text(" ")) else (ps[0] if ps else None)
        note = None
        if desc and re.match(r"(acquired|merged|ipo)\b", desc, re.I):
            note, desc = desc, (ps[0] if ps else None)
        long = ps[0] if ps and ps[0] != desc else None
        site = next((a["href"] for a in box.select("a[href^=http]") if not SKIP.search(a["href"])), None)
        out.append(rec(name, desc, site, PRIMARY, SOURCE_URL, scraped_at, status="Exited" if note else st, exit_note=note,
                       long_description=long, profile_url=u))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Draper Triangle companies")
    finish(out, "drapertriangle", ("description", "website", "everywhere_tags"))


if __name__ == "__main__":
    main()
