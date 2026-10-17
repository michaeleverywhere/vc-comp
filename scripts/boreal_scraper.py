#!/usr/bin/env python3
"""Boreal Ventures portfolio scraper -> boreal_companies.json
Source: https://boreal.vc/ — Webflow portfolio modals: company name, description,
founders, investment date, investment focus and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://boreal.vc/"
PRIMARY = "Boreal Ventures"


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
    for it in s.select("div.collection-item-5.w-dyn-item"):
        nm = txt(it.select_one(".company-hidden-sr-only"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x).replace("\xa0", " ") for x in it.stripped_strings if clean(x)]
        def lab(l):
            return p[p.index(l) + 1] if l in p and p.index(l) + 1 < len(p) else None
        desc = next((x for x in p if x != nm and len(x) > 25), None)
        web = next((site(a) for a in it.select("a[href^=http]") if site(a)), None)
        fo = lab("INVESTMENT FOCUS")
        out.append(rec(nm, desc, web, PRIMARY, SOURCE_URL, scraped_at, founders=lab("FOUNDERS"), invested_year=lab("INVESTMENT DATE"),
                       sectors=[fo] if fo else []))
    finish(out, "boreal", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
