#!/usr/bin/env python3
"""Better Capital portfolio scraper -> bettercapital_companies.json
Source: https://www.bettercapital.vc/portfolio — server-rendered portfolio
table: each row has the company name linked to its website and a one-line
description.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social
from _d50_common import rec, finish

SOURCE_URL = "https://www.bettercapital.vc/portfolio"
PRIMARY = "Better Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for tr in soup.select("tr"):
        td = tr.find_all("td")
        if len(td) < 2 or not td[0].find("a"):
            continue
        a = td[0].find("a")
        href = a.get("href") or ""
        out.append(rec(a.get_text(" ", strip=True), td[1].get_text(" ", strip=True),
                       href if href.startswith("http") and not is_social(href) else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "bettercapital", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
