#!/usr/bin/env python3
"""Beta Boom portfolio scraper -> betaboom_companies.json
Source: https://www.betaboom.com/portfolio — Webflow companies list: company name, sectors and
acquired status."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.betaboom.com/portfolio"
PRIMARY = "Beta Boom"


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
    for it in s.select("div.w-dyn-item"):
        nm = txt(it.select_one("h2.item-companies_title"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in it.stripped_strings if clean(x)][1:]
        st = [x for x in p if x.lower() in ("acquired", "exited", "ipo")]
        sec = [x for x in p if x not in st]
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sec,
                       status="exited" if st else None))
    finish(out, "betaboom", ("everywhere_tags",))


if __name__ == "__main__":
    main()
