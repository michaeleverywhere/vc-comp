#!/usr/bin/env python3
"""Rally Ventures portfolio scraper -> rally_companies.json
Source: https://www.rallyventures.com/ — investment panes (hidden data blocks):
title, subtitle, website, description, and exit facts (Acquired / IPO Date).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.rallyventures.com/"
PRIMARY = "Rally Ventures"


def facts_of(strings):
    f = {}
    for i, s in enumerate(strings[:-1]):
        n = strings[i + 1]
        if n.startswith(":"):
            f[s.strip().lower()] = n.lstrip(": ").strip()
    return f


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for d in soup.select(".data"):
        g = lambda k: (lambda e: clean(e.get_text(" ", strip=True)) if e else None)(d.select_one(f'[data-source="{k}"]'))
        name = g("title")
        if not name:
            continue
        t = d.select_one('[data-source="text"]')
        strs = [clean(x) for x in t.stripped_strings] if t else []
        f = facts_of(strs)
        desc = " ".join(x for x in strs if not x.startswith(":") and x.strip().lower() not in f) or None
        a = d.select_one('a[data-source="link"][href]')
        status = "ipo" if "ipo date" in f else ("acquired" if "acquired" in f else "active")
        out.append(rec(name, desc, a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at, tagline=g("subtitle"),
                       status=status, acquirer=f.get("acquired"), exit_date=f.get("date") or f.get("ipo date"),
                       exit_year=year_of(f.get("date") or f.get("ipo date")), ipo_valuation=f.get("valuation at ipo"),
                       ticker=f.get("ticker symbol")))
    finish(out, "rally", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
