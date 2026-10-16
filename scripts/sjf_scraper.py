#!/usr/bin/env python3
"""SJF Ventures portfolio scraper -> sjf_companies.json
Source: https://sjfventures.com/our-portfolio/ — WordPress grid blocks
(`.xgrid_Full_InnerInner`): company name (h3), description and website
link (malformed "http://https://" prefixes are repaired).
"""
import os, re, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://sjfventures.com/our-portfolio/"
PRIMARY = "SJF Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".xgrid_Full_InnerInner"):
        h = it.find("h3")
        if not h or not clean(h.get_text()):
            continue
        p = it.find("p")
        a = it.select_one("a.companyWebsite[href]")
        href = re.sub(r"^https?://(?=https?://)", "", a["href"].strip()) if a else ""
        href = href if re.match(r"https?://[^/]+\.", href) and not is_social(href) else None
        out.append(rec(h.get_text(" ", strip=True), p.get_text(" ", strip=True) if p else None, href,
                       PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "sjf", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
