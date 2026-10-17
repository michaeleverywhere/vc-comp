#!/usr/bin/env python3
"""RunwayVC portfolio scraper -> runwayvc_companies.json
Source: https://runway.vc/portfolio — Next.js portfolio tiles: company name, fund
tag and one-line description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://runway.vc/portfolio"
PRIMARY = "RunwayVC"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # decode bytes as UTF-8 explicitly (some servers omit the charset -> mojibake)
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for a in s.select("a.portfolio-tile"):
        nm = txt(a.select_one(".portfolio-tile-name"))
        if not nm:
            continue
        tag = a.select_one(".pfund-tag")
        out.append(rec(nm, txt(a.select_one(".portfolio-tile-oneline")), site(a), PRIMARY, SOURCE_URL, scraped_at, fund=("Fund " + txt(tag)) if tag is not None and txt(tag) else None))
    finish(out, "runwayvc", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
