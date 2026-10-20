#!/usr/bin/env python3
"""Proeza Ventures portfolio scraper -> proezaventures_companies.json
Source: https://www.proezaventures.com/our-portfolio/ — Proeza's Elementor flip-box portfolio:
company name, Proeza's one-line description and the company website ("Visit Website")."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.proezaventures.com/our-portfolio/"
PRIMARY = "Proeza Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for box in s.select(".elementor-flip-box"):
        t = box.select_one(".elementor-flip-box__layer__title")
        name = clean(t.get_text(" ", strip=True)) if t else None
        if not name:
            continue
        d = box.select_one(".elementor-flip-box__layer__description")
        a = box.select_one("a[href^=http]")
        url = a["href"] if a and not is_social(a["href"]) and "proezaventures.com" not in a["href"] else None
        out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None, url, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 10:
        raise SystemExit(f"FATAL: only {len(out)} Proeza companies")
    finish(out, "proezaventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
