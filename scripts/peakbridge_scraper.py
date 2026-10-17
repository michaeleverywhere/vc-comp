#!/usr/bin/env python3
"""PeakBridge portfolio scraper -> peakbridge_companies.json
Source: https://peakbridge.vc/portfolio/ — JetEngine portfolio listing: company name,
one-line description and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://peakbridge.vc/portfolio/"
PRIMARY = "PeakBridge"


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
    for w in s.select(".jet-engine-listing-overlay-wrap"):
        parts = [clean(x) for x in w.stripped_strings if clean(x)]
        if not parts:
            continue
        nm = parts[0]
        out.append(rec(nm, parts[1] if len(parts) > 1 else None, None, PRIMARY, SOURCE_URL, scraped_at,
                       detail_url=w.get("data-url")))
    finish(out, "peakbridge", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
