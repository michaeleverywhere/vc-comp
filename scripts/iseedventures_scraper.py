#!/usr/bin/env python3
"""iSeed Ventures portfolio scraper -> iseedventures_companies.json
Source: https://www.iseed.vc/portfolio-investments — iSeed's Google Sites portfolio grid: every
company name (caption under each logo) with the company website the logo links to."""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urlparse, parse_qs
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.iseed.vc/portfolio-investments"
PRIMARY = "iSeed Ventures"
SKIP = {"report abuse", "page details", "page updated", "google sites", "portfolio", "skip to main content",
        "skip to navigation", "search this site", "embedded files"}


def _target(href):
    if "google.com/url" in href:
        q = parse_qs(urlparse(href).query).get("q")
        return q[0] if q else None
    return href


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    s = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    main_ = s.select_one('body') or s
    out, last = [], None
    for el in main_.find_all(["a", "p"]):
        if el.name == "a" and el.select_one("img"):
            last = _target(el.get("href") or "")
            continue
        if el.name == "p":
            name = clean(el.get_text("", strip=True))
            if not name or name.lower() in SKIP or len(name) > 60:
                continue
            url = last if last and last.startswith("http") and not is_social(last) and "iseed.vc" not in last else None
            out.append(rec(name, None, url, PRIMARY, SOURCE_URL, scraped_at))
            last = None
    if len(out) < 30:
        raise SystemExit(f"FATAL: only {len(out)} iSeed companies")
    finish(out, "iseedventures", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
