#!/usr/bin/env python3
"""Archetype portfolio scraper -> archetype_companies.json
Source: https://www.archetype.fund/portfolio — Webflow portfolio list: company name, website and
acquisition note."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.archetype.fund/portfolio"
PRIMARY = "Archetype"


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
    for it in s.select("div.collection-list-3 > div"):
        p = [clean(x) for x in it.stripped_strings if clean(x)]
        if not p or p[0].lower() in seen or p[0].startswith("Acquired"):
            continue
        seen.add(p[0].lower())
        note = next((x for x in p[1:] if x.startswith("Acquired")), None)
        a = it.select_one("a[href^=http]")
        out.append(rec(p[0], None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, exit_note=note,
                       status="exited" if note else None))
    finish(out, "archetype", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
