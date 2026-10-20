#!/usr/bin/env python3
"""Neon Fund portfolio scraper -> neonfund_companies.json
Source: https://neon.fund/investments/ — WordPress investments grid: company name (the card
link's title attribute, as Neon writes it — several are domain-style names), Neon's one-line
description, website, founder names, the fund the company sits in (the page's own Pre-fund /
Fund I / Fund II / Fund III filter) and the "• Exited" marker (-> status)."""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://neon.fund/investments/"
PRIMARY = "Neon Fund"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    funds = {a.get("data-name"): clean(a.get_text(" ", strip=True))
             for a in s.select(".porfopgs2-filter-list a[data-name]") if a.get("data-name") != "all"}
    out = []
    for g in s.select("div.porfopgs3-grid-item"):
        a = g.select_one("a[title]")
        if not a:
            continue
        name = clean(a.get("title"))
        if name and re.fullmatch(r"[A-Z0-9.-]+\.[A-Z]{2,}", name):
            name = name.lower()  # all-caps domain-style names
        t1 = g.select_one(".stcfbx-text-1")
        desc = clean(t1.get_text(" ", strip=True)) if t1 else None
        if desc and name:
            desc = clean(re.sub(r"^" + re.escape(name.split(".")[0]) + r"[\w.]*\s*:?\s+", "", desc, flags=re.I)) or desc
        founders = [clean(x.get_text(" ", strip=True)) for x in g.select(".stcfbx-text-2 a")]
        fund = next((funds[c] for c in g.get("class", []) if c in funds), None)
        t3 = g.select_one(".stcfbx-text-3")
        exited = bool(t3 and "exited" in t3.get_text(" ", strip=True).lower())
        url = a.get("href")
        if url and is_social(url):
            url = None
        out.append(rec(name, desc, url, PRIMARY, SOURCE_URL, scraped_at, founders=[f for f in founders if f],
                       fund=fund, status="exited" if exited else "active"))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Neon companies")
    finish(out, "neonfund", ("description", "company_url", "founders", "fund", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
