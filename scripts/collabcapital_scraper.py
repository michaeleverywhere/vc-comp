#!/usr/bin/env python3
"""Collab Capital portfolio scraper -> collabcapital_companies.json
Source: https://www.collab.capital/portfolio — Webflow CMS `.cms_list-item`
cards: company name, sector tag, founder, location, fund and a detail page
/companies/<slug>. (Collab Capital is a distinct firm from Collaborative Fund.)
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.collab.capital/portfolio"
PRIMARY = "Collab Capital"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    for e in soup.select(".w-condition-invisible"):
        e.decompose()
    out = []
    for it in soup.select(".cms_list-item"):
        nm = txt(it.select_one(".company_name"))
        if not nm:
            continue
        tags = [txt(t) for t in it.select(".company-tag [fs-list-field]")]
        a = it.select_one("a.company_content[href]")
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[t for t in tags if t],
                       founders=txt(it.select_one(".company_founder")), location=txt(it.select_one(".company_location")),
                       fund=txt(it.select_one(".card_info")), detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "collabcapital", ("founders", "location", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
