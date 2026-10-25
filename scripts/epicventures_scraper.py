#!/usr/bin/env python3
"""EPIC Ventures portfolio scraper -> epicventures_companies.json
Source: https://epicvc.com/all — EPIC Ventures, Salt Lake City early-stage venture firm (Ancestry, PillPack,
Everspin...). The Squarespace portfolio lists every company by name; the site's own filter pages (/active, /exited,
/saas, /healthcare, /security, /futureofwork, /other) give each company's Active/Exited status and EPIC sector.
Company names only (the site links out to third-party profiles, which are not stored)."""
import os, sys, re
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_many, clean
from _d50_common import rec, finish

BASE = "https://epicvc.com"
SOURCE_URL = "https://epicvc.com/all"
PRIMARY = "EPIC Ventures"
FILTERS = {"active": "Active", "exited": "Exited"}
SECTORS = {"saas": "SaaS", "healthcare": "Healthcare", "security": "Security", "futureofwork": "Future of Work", "other": "Other"}


def names(html):
    s = BeautifulSoup(html, "html.parser")
    out = []
    for b in s.select("div.sqs-html-content"):
        links = b.select("p a[href]")
        if not links or all(a["href"].startswith("/") for a in links):
            continue
        for a in links:
            n = clean(a.get_text(" "))
            if n and not a["href"].startswith("/"):
                out.append(n)
    return out


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    allnames = names(fetch(SOURCE_URL))
    pages = fetch_many([f"{BASE}/{k}" for k in list(FILTERS) + list(SECTORS)], workers=3)
    status, sector = {}, {}
    for k, v in FILTERS.items():
        for n in names(pages.get(f"{BASE}/{k}") or ""):
            status[n.lower()] = v
    for k, v in SECTORS.items():
        for n in names(pages.get(f"{BASE}/{k}") or ""):
            sector.setdefault(n.lower(), v)
    out, seen = [], set()
    for n in allnames:
        if n.lower() in seen:
            continue
        seen.add(n.lower())
        out.append(rec(n, None, None, PRIMARY, SOURCE_URL, scraped_at,
                       status=status.get(n.lower()), epic_sector=sector.get(n.lower())))
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} EPIC Ventures companies")
    finish(out, "epicventures", ("status", "epic_sector", "everywhere_tags"))


if __name__ == "__main__":
    main()
