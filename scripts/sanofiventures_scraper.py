#!/usr/bin/env python3
"""Sanofi Ventures portfolio scraper -> sanofiventures_companies.json
Source: https://www.sanofiventures.com/portfolio/ — Drupal portfolio grid; each
card's modal trigger carries the company name (data-title) and its modal gives
company type (Public/Private/Acquired...), location, website, intro line and
body description.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.sanofiventures.com/portfolio/"
PRIMARY = "Sanofi Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select("a.modal-trigger[data-title]"):
        m = soup.find(id=(a.get("data-bs-target") or "").lstrip("#"))
        if not m:
            continue
        g = lambda f: clean(m.select_one(f".field--name-field-{f}").get_text(" ", strip=True)) if m.select_one(f".field--name-field-{f}") else None
        w = m.select_one(".field--name-field-company-website a[href]")
        site = w["href"] if w and w["href"].startswith("http") and not is_social(w["href"]) else None
        body = m.select_one(".field--name-body")
        desc = clean(body.get_text(" ", strip=True)) if body else None
        intro = g("intro-text")
        typ = g("company-type")
        st = (typ or "").lower()
        out.append(rec(a["data-title"], desc or intro, site, PRIMARY, SOURCE_URL, scraped_at, tagline=intro,
                       hq_location=g("company-location"), company_status=typ,
                       status="acquired" if "acquired" in st else "ipo" if st == "public" else "active" if st == "private" else None))
    finish(out, "sanofiventures", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
