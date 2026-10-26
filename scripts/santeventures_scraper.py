#!/usr/bin/env python3
"""Santé Ventures portfolio scraper -> santeventures_companies.json
Source: https://sante.com/portfolio/ — Santé Ventures (Austin, TX), early-stage healthcare venture firm
investing across biology, medicine and information. The WordPress site publishes its portfolio as REST post type
`companies`: one entry per company with its name and sector taxonomy (no description or website is published)."""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import html_text
import requests
from _d50_common import rec, finish

SOURCE_URL = "https://sante.com/portfolio/"
ORIGIN = "https://sante.com"
PRIMARY = "Santé Ventures"
UA = {"User-Agent": "Mozilla/5.0 Chrome/124"}  # the site's WAF returns 520 to the shared desktop UA string


def wp(path):
    out, page = [], 1
    while True:
        r = requests.get(f"{ORIGIN}/wp-json/wp/v2/{path}?per_page=100&page={page}", headers=UA, timeout=45)
        r.raise_for_status()
        out += r.json()
        if page >= int(r.headers.get("X-WP-TotalPages") or 1):
            return out
        page += 1


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    sec = {t["id"]: html_text(t["name"]) for t in wp("sectors")}
    out = []
    for p in wp("companies"):
        sectors = [sec[i] for i in p.get("sectors") or [] if sec.get(i)]
        out.append(rec(html_text(p["title"]["rendered"]), None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sectors))
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} Santé companies")
    finish(out, "santeventures", ("sectors", "everywhere_tags"))


if __name__ == "__main__":
    main()
