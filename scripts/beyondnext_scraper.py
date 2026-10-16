#!/usr/bin/env python3
"""Beyond Next Ventures portfolio scraper -> beyondnext_companies.json
Source: https://beyondnextventures.com/portfolio/ — server-rendered (WordPress)
list of `li.col5` cards: company name, one-line description and website link.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://beyondnextventures.com/portfolio/"
PRIMARY = "Beyond Next Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for li in soup.select("li"):
        nm = li.select_one(".company-name")
        if not nm:
            continue
        a = li.select_one("a.block-link[href]")
        href = a["href"] if a else ""
        d = li.select_one(".description")
        out.append(rec(nm.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None,
                       href if href.startswith("http") and not is_social(href) else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "beyondnext", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
