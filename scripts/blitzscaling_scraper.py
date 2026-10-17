#!/usr/bin/env python3
"""Blitzscaling Ventures portfolio scraper -> blitzscaling_companies.json
Source: https://www.blitzscalingvc.com/portfolio — Wix portfolio repeater: company name,
one-line description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.blitzscalingvc.com/portfolio"
PRIMARY = "Blitzscaling Ventures"


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
    for it in s.select("div._FiCX"):
        ts = [txt(x) for x in it.select(".wixui-rich-text") if txt(x)]
        if not ts:
            continue
        a = next((x for x in it.select("a[href^='http']") if site(x)), None)
        out.append(rec(ts[0], ts[1] if len(ts) > 1 else None, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "blitzscaling", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
