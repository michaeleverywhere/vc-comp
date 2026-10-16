#!/usr/bin/env python3
"""Mashup Ventures portfolio scraper -> mashup_companies.json
Source: https://www.mashupventures.co/portfolio/ — static catalog of
`a.company-card` cards: company name (h3, as published, mostly Korean),
description and sector tags ("Consumer · Commerce"). No websites listed. Card hrefs are relative to <base href="../"> (site root).
"""
import os, sys
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://www.mashupventures.co/portfolio/"
PRIMARY = "Mashup Ventures"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for a in soup.select("a.company-card"):
        h = a.find("h3")
        if not h:
            continue
        d = a.select_one(".card-description")
        t = a.select_one(".card-tags")
        tags = [clean(x) for x in t.get_text(strip=True).split("·") if clean(x)] if t else []
        out.append(rec(h.get_text(" ", strip=True), d.get_text(" ", strip=True) if d else None, None,
                       PRIMARY, SOURCE_URL, scraped_at, sectors=tags, detail_url=urljoin("https://www.mashupventures.co/", a["href"])))
    finish(out, "mashup", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
