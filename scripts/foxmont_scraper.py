#!/usr/bin/env python3
"""Foxmont Capital Partners portfolio scraper -> foxmont_companies.json
Source: https://foxmontcapital.com/ — Framer static page; portfolio cards
show company name (h3, "Heading - Large") followed by a one-line description.
Framer breakpoint duplicates are removed by name.
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean
from _d50_common import rec, finish

SOURCE_URL = "https://foxmontcapital.com/"
PRIMARY = "Foxmont Capital Partners"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch(SOURCE_URL), "html.parser")
    out = []
    for h in soup.find_all("h3"):
        box = h.find_parent(attrs={"data-framer-name": "Heading - Large"})
        if not box:
            continue
        name = clean(h.get_text(" ", strip=True))
        if not name:
            continue
        nxt = box.find_next_sibling(attrs={"data-framer-name": True})
        desc = clean(nxt.get_text(" ", strip=True)) if nxt and nxt.find("p") else None
        out.append(rec(name, desc, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "foxmont", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
