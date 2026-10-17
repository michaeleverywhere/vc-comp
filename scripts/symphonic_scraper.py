#!/usr/bin/env python3
"""Symphonic Capital portfolio scraper -> symphonic_companies.json
Source: https://www.symphoniccapital.com/portfolio-companies — Webflow/Finsweet cards:
company name, industry, one-line description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.symphoniccapital.com/portfolio-companies"
PRIMARY = "Symphonic Capital"


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
    for it in s.select(".w-dyn-item:has(a.company-item_link-wrapper)"):
        a = it.select_one("a.company-item_link-wrapper")
        t = it.select_one("[fs-cmsfilter-field='title']")
        nm = txt(t)
        if not nm:
            continue
        d = t.find_next_sibling("div")
        ind = [txt(x) for x in it.select("[fs-cmsfilter-field='industry']") if txt(x)]
        out.append(rec(nm, txt(d) if d and not d.get("class") else None, site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=ind))
    finish(out, "symphonic", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
