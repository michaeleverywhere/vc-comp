#!/usr/bin/env python3
"""Robert Bosch Venture Capital (Bosch Ventures) portfolio scraper -> bosch_companies.json
Source: https://bosch.ventures/portfolio/ — server-rendered teasers: company name,
subtitle (one-liner), full description paragraph and external website link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://bosch.ventures/portfolio/"
PRIMARY = "Bosch Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch_response(SOURCE_URL).content, "html.parser")  # bytes: server omits charset
    out = []
    for t in soup.select("div.A-ItemTeaser"):
        h = t.select_one(".A-ItemTeaser__title")
        if not h:
            continue
        a = t.select_one("a.A-ItemTeaser__linkRegion")
        sub = t.select_one(".A-ItemTeaser__subtitle")
        d = t.select_one(".A-ItemTeaser__description")
        url = (a.get("href") or "").strip() if a else None
        out.append(rec(h.get_text(" ", strip=True), clean(d.get_text(" ", strip=True)) if d else None,
                       url if url and url.startswith("http") and "bosch.ventures" not in url else None,
                       PRIMARY, SOURCE_URL, scraped_at, tagline=clean(sub.get_text()) if sub else None))
    finish(out, "bosch", ("description", "company_url", "tagline", "everywhere_tags"))


if __name__ == "__main__":
    main()
