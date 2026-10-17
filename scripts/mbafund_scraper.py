#!/usr/bin/env python3
"""The MBA Fund portfolio scraper -> mbafund_companies.json
Source: https://www.thembafund.com/portfolio — Webflow portfolio cards: company name and
exit indicator (the site lists names only)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.thembafund.com/portfolio"
PRIMARY = "The MBA Fund"


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
    for it in s.select("div.collection-item-3"):
        nm = txt(it.select_one("h3"))
        if not nm:
            continue
        ex = txt(it.select_one(".exit-indicator"))
        out.append(rec(nm, None, site(it.select_one("a[href^='http']")), PRIMARY, SOURCE_URL, scraped_at,
                       exit_note=ex, status="acquired" if ex and "acqui" in ex.lower() else ("exited" if ex else None)))
    finish(out, "mbafund", ("everywhere_tags",))


if __name__ == "__main__":
    main()
