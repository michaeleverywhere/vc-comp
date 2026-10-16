#!/usr/bin/env python3
"""Blue Bear Capital portfolio scraper -> bluebear_companies.json
Source: https://bluebearcap.com/portfolio-companies/ — WordPress grid of
company panels (`.tgr-right`): name (h3), description paragraph and website.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://bluebearcap.com/portfolio-companies/"
PRIMARY = "Blue Bear Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for c in soup.select(".tgr-right"):
        h = c.select_one(".tgr-member-title h3")
        if not h:
            continue
        d = c.select_one(".tgr-member-content")
        a = c.select_one(".tgr-member-social a[href^=http]")
        href = a["href"] if a and not is_social(a["href"]) else None
        out.append(rec(h.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None, href,
                       PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "bluebear", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
