#!/usr/bin/env python3
"""Seven Seven Six (776) portfolio scraper -> sevensevensix_companies.json
Source: https://www.sevensevensix.com/portfolio — the portfolio grid's own data feed (the page's
React app loads it from 776's Cerebro backend, api.cerebro.ai/sevensevensix/portfolio): company
name exactly as 776 prints it (including its own notes such as "(FKA …)" / "(now …)") and website."""
import os, sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.sevensevensix.com/portfolio"
FEED = "https://api.cerebro.ai/sevensevensix/portfolio"
PRIMARY = "Seven Seven Six"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    data = fetch(FEED, as_json=True)
    out = []
    for x in data:
        name = clean(x.get("name"))
        if not name:
            continue
        url = clean(x.get("website"))
        if url and is_social(url):
            url = None
        out.append(rec(name, None, url, PRIMARY, SOURCE_URL, scraped_at))
    if len(out) < 60:
        raise SystemExit(f"FATAL: only {len(out)} Seven Seven Six companies")
    finish(out, "sevensevensix", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
