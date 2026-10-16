#!/usr/bin/env python3
"""La Famiglia portfolio scraper -> lafamiglia_companies.json
Source: https://www.lafamiglia.vc/founders — Webflow "rolladex" list: company
name, description, website.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.lafamiglia.vc/founders"
PRIMARY = "La Famiglia"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for it in soup.select(".rolladexitem"):
        h = it.select_one(".companydropdowntoggle .headlinesmall")
        if not h:
            continue
        p = it.select_one(".companydropdownlist p")
        a = it.select_one(".companydropdownlist a[href^=http]")
        out.append(rec(h.get_text(" ", strip=True), p.get_text(" ", strip=True) if p else None, a["href"] if a else None,
                       PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "lafamiglia")


if __name__ == "__main__":
    main()
