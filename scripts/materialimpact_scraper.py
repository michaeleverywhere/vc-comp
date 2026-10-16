#!/usr/bin/env python3
"""Material Impact portfolio scraper -> materialimpact_companies.json
Source: https://www.materialimpact.com/companies/ — WordPress company grid
with popouts (`.popout`): company name (h3), website link and description.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.materialimpact.com/companies/"
PRIMARY = "Material Impact"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for p in soup.select(".popout"):
        h = p.select_one(".top h3")
        if not h or not clean(h.get_text()):
            continue
        a = p.select_one(".top .web a[href]")
        href = a["href"] if a and a["href"].startswith("http") and not is_social(a["href"]) else None
        d = p.select_one(".middle p")
        out.append(rec(h.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None, href,
                       PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "materialimpact", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
