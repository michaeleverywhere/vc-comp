#!/usr/bin/env python3
"""Innovation Endeavors portfolio scraper -> innovationendeavors_companies.json
Source: https://www.innovationendeavors.com/companies — "All companies" list:
"<a href=website>Name</a> — description" per <li>.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.innovationendeavors.com/companies"
PRIMARY = "Innovation Endeavors"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for li in soup.select("li"):
        a = li.find("a", href=True)
        txt = clean(li.get_text(" ", strip=True)) or ""
        if not a or "—" not in txt:
            continue
        name = clean(a.get_text(" ", strip=True))
        desc = clean(txt.split("—", 1)[1])
        href = a["href"]
        out.append(rec(name, desc, href if href.startswith("http") and "innovationendeavors" not in href else None,
                       PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "innovationendeavors", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
