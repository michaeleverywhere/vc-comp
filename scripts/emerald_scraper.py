#!/usr/bin/env python3
"""Emerald Technology Ventures portfolio scraper -> emerald_companies.json
Source: https://emerald.vc/portfolio — Portfolio cards: company name, tagline and exited flag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://emerald.vc/portfolio"
PRIMARY = "Emerald Technology Ventures"


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
    for a in s.select("a.company-card"):
        p = [clean(x) for x in a.stripped_strings if clean(x)]
        if not p or p[0].lower() in seen:
            continue
        seen.add(p[0].lower())
        ex = any(x.lower() == "exited" for x in p)
        d = next((x for x in p[1:] if x.lower() != "exited"), None)
        out.append(rec(p[0], d, None, PRIMARY, SOURCE_URL, scraped_at, status="exited" if ex else None))
    finish(out, "emerald", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
