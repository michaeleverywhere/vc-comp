#!/usr/bin/env python3
"""Activant Capital portfolio scraper -> activant_companies.json
Source: https://activantcapital.com/ — portfolio logo wall: each cell has the
company name (aria-label), website link, one-line caption and an "Exit" pill for
realized investments (caption then describes the exit).
"""
import os, sys
from datetime import datetime, timezone
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, clean
from _d50_common import rec, finish

SOURCE_URL = "https://activantcapital.com/"
PRIMARY = "Activant Capital"


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    soup = BeautifulSoup(fetch_response(SOURCE_URL).content, "html.parser")
    out = []
    for a in soup.select("a.logo-cell"):
        name = clean(a.get("aria-label"))
        if not name:
            continue
        cap = a.select_one(".caption")
        cap = clean(cap.get_text(" ", strip=True)) if cap else None
        exited = a.select_one(".exit-pill") is not None
        href = a.get("href") or ""
        out.append(rec(name, None if exited else cap, href if href.startswith("http") else None, PRIMARY, SOURCE_URL, scraped_at,
                       status="exited" if exited else "active", exit_note=cap if exited else None))
    finish(out, "activant", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
