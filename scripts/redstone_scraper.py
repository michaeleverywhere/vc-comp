#!/usr/bin/env python3
"""Redstone portfolio scraper -> redstone_companies.json
Source: https://redstone.vc/portfolio — Webflow portfolio list: company name, sectors and
exited flag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://redstone.vc/portfolio"
PRIMARY = "Redstone"


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
    for it in s.select("div.portfolio-collection-list > div"):
        nm = txt(it.select_one("div.fs-name-source"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in it.stripped_strings if clean(x) and "text inside of a div" not in clean(x) and clean(x) != "No items found."]
        ex = "EXITED" in p
        sec = [x for x in p if x not in (nm, "EXITED")]
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sec, status="exited" if ex else None))
    finish(out, "redstone", ("everywhere_tags",))


if __name__ == "__main__":
    main()
