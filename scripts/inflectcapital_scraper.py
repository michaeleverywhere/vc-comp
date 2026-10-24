#!/usr/bin/env python3
"""Inflect Capital portfolio scraper -> inflectcapital_companies.json
Source: https://www.inflect.health/capital — Inflect Capital, the pre-seed to Series A healthcare venture arm of
Inflect Health. The "Meet our portfolio" Webflow table (a.portfoliodiv) gives each company's name, founder, overview
and website link."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.inflect.health/capital"
PRIMARY = "Inflect Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select("a.portfoliodiv"):
        n = a.select_one(".portfolio-name")
        name = clean(n.get_text(" ", strip=True)) if n else None
        if not name:
            continue
        d = a.select_one(".portfolio-overview")
        f = [clean(x.get_text(" ", strip=True)) for x in a.select(".founder-name")]
        out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None, a.get("href"),
                       PRIMARY, SOURCE_URL, scraped_at, sectors=["Healthcare"],
                       founders="; ".join(x for x in f if x) or None))
    if len(out) < 12:
        raise SystemExit(f"FATAL: only {len(out)} Inflect Capital companies")
    finish(out, "inflectcapital", ("description", "company_url", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
