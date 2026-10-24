#!/usr/bin/env python3
"""Context Ventures portfolio scraper -> contextventures_companies.json
Source: https://www.contextvc.com/context-ventures — Context Ventures (Context VC), early-stage venture firm backing
consumer brands and military-veteran entrepreneurs. The Squarespace gallery blocks list each company (slide title +
website link) under the page's section headings: Consumer Brands, Military Entrepreneurs, Previous Investments."""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup, NavigableString

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.contextvc.com/context-ventures"
PRIMARY = "Context Ventures"
GROUPS = {"CONSUMER BRANDS": "Consumer Brands", "MILITARY ENTREPRENEURS": "Military Entrepreneurs",
          "PREVIOUS INVESTMENTS": "Previous Investments"}


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out, group = [], None
    for el in soup.descendants:
        if isinstance(el, NavigableString):
            t = (clean(str(el)) or "").upper()
            if t in GROUPS and el.parent.name not in ("script", "style"):
                group = GROUPS[t]
            continue
        if el.name == "div" and "slide" in (el.get("class") or []) and group:
            t = el.select_one(".image-slide-title")
            name = clean(t.get_text(" ", strip=True)) if t else None
            if not name:
                continue
            a = el.select_one("a[href]")
            out.append(rec(name, None, a["href"] if a else None, PRIMARY, SOURCE_URL, scraped_at,
                           portfolio_group=group))
    if len(out) < 15:
        raise SystemExit(f"FATAL: only {len(out)} Context Ventures companies")
    finish(out, "contextventures", ("company_url", "portfolio_group", "everywhere_tags"))


if __name__ == "__main__":
    main()
