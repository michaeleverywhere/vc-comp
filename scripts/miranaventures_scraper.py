#!/usr/bin/env python3
"""Mirana Ventures portfolio scraper -> miranaventures_companies.json
Source: https://www.mirana.xyz/portfolio — Mirana Ventures, crypto / digital-asset venture investor; the Webflow
portfolio page's "Companies" collection gives each portfolio company's name and website. The page's separate
"Funds" collection (Mirana's LP commitments to other venture funds) is not companies and is skipped."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, clean_url
from _d50_common import rec, finish

SOURCE_URL = "https://www.mirana.xyz/portfolio"
PRIMARY = "Mirana Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    label = next((d for d in soup.select("div.all-uppercase.text-size-small")
                  if clean(d.get_text(" ", strip=True)) and clean(d.get_text(" ", strip=True)).lower() == "companies"), None)
    if label is None:
        raise SystemExit("FATAL: Companies section not found")
    lst = label.find_next("div", class_="w-dyn-list")  # first collection after the "Companies" label
    out = []
    for a in lst.select("a.gallery6_card"):
        n = a.select_one("div.gallery6_card-info div.all-uppercase")
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name:
            continue
        out.append(rec(name, None, clean_url(a.get("href")), PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 20:
        raise SystemExit(f"FATAL: only {len(out)} Mirana companies")
    finish(out, "miranaventures", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
