#!/usr/bin/env python3
"""Album VC portfolio scraper -> album_companies.json
Source: https://www.album.vc/ — WordPress home page portfolio list
(`.portfolio-list-block li a`): company names with website links where
published. Names and websites only.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.album.vc/"
PRIMARY = "Album VC"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select(".portfolio-list-block li a"):
        nm = clean(a.get_text(" ", strip=True))
        if not nm:
            continue
        href = (a.get("href") or "").strip()
        out.append(rec(nm, None, href if href.startswith("http") and not is_social(href) else None,
                       PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "album", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
