#!/usr/bin/env python3
"""Twin Path Ventures portfolio scraper -> twinpath_companies.json
Source: https://www.twinpath.vc/portfolio — Framer portfolio list: company name and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.twinpath.vc/portfolio"
PRIMARY = "Twin Path Ventures"


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
    seen = set()
    for a in s.select("a[href^=http]"):
        h = a.select_one("h3")
        nm = txt(h)
        if not nm or nm.lower() in seen or len(nm) > 40:
            continue
        seen.add(nm.lower())
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "twinpath", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
