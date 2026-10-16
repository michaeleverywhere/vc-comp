#!/usr/bin/env python3
"""Twelve Below portfolio scraper -> twelvebelow_companies.json
Source: https://www.twelvebelow.co/portfolio — Webflow CMS
`.portfolio-cms-item`: "<Company>, founded by <founders>" line (company link
= website; founder names) and a one-line description.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.twelvebelow.co/portfolio"
PRIMARY = "Twelve Below"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".portfolio-cms-item"):
        line = it.select_one(".founders-list")
        if not line:
            continue
        first = line.find("a", recursive=False) or line.find("a")
        name = clean(first.get_text(" ", strip=True)) if first else None
        if not name:
            continue
        href = first.get("href") or ""
        founders = [clean(a.get_text(" ", strip=True)) for a in line.select(".founder-item a")]
        d = it.select_one("p.subtle")
        out.append(rec(name, clean(d.get_text(" ", strip=True)) if d else None,
                       href if href.startswith("http") and not is_social(href) else None, PRIMARY, SOURCE_URL, scraped_at,
                       founders=", ".join(f for f in founders if f) or None))
    finish(out, "twelvebelow", ("description", "company_url", "founders", "everywhere_tags"))


if __name__ == "__main__":
    main()
