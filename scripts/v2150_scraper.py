#!/usr/bin/env python3
"""2150 portfolio scraper -> v2150_companies.json
Source: https://www.2150.vc/investments — Framer investments page: company name and
description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.2150.vc/investments"
PRIMARY = "2150"


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
    for d in s.select("div.framer-1ywe3gc"):
        p = [clean(x) for x in d.stripped_strings if clean(x)]
        if len(p) < 1 or p[0].lower() in seen:
            continue
        seen.add(p[0].lower())
        out.append(rec(p[0], p[1] if len(p) > 1 else None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "v2150", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
