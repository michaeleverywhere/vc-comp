#!/usr/bin/env python3
"""Industrious Ventures portfolio scraper -> industrious_companies.json
Source: https://industrious.vc/portfolio/ — portfolio cards (`div.customer-item`):
company name (logo alt), sector label, summary, website and acquired sticker."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://industrious.vc/portfolio/"
PRIMARY = "Industrious Ventures"


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
    for it in s.select("div.customer-item"):
        img = it.select_one(".customer-image img")
        nm = clean(img.get("alt")) if img else None
        if not nm:
            continue
        sm = it.select_one(".customer-item-summary")
        if sm:
            for f in sm.select(".customer-footer"):
                f.extract()
        lab = txt(it.select_one(".customer-item-label"))
        stk = txt(it.select_one(".customer-sticker"))
        out.append(rec(nm, txt(sm), site(it.select_one("a.customer-item-link")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[lab] if lab else [], status="acquired" if stk and "acqui" in stk.lower() else None))
    finish(out, "industrious", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
