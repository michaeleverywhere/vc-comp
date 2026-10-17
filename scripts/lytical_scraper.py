#!/usr/bin/env python3
"""Lytical Ventures portfolio scraper -> lytical_companies.json
Source: https://www.lyticalventures.com/companies — Wix companies repeater: company name
(logo alt text), description and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.lyticalventures.com/companies"
PRIMARY = "Lytical Ventures"


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
    for it in s.select(".wixui-repeater__item"):
        a = next((x for x in it.select("a[href*='/companies/']") if x.select_one("img")), None)
        nm = clean(a.select_one("img").get("alt")) if a else None
        if not nm:
            continue
        ts = [txt(x) for x in it.select(".wixui-rich-text") if txt(x)]
        out.append(rec(nm, ts[0] if ts else None, None, PRIMARY, SOURCE_URL, scraped_at, detail_url=a["href"]))
    finish(out, "lytical", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
