#!/usr/bin/env python3
"""Lumir Ventures portfolio scraper -> lumir_companies.json
Source: https://www.lumir.vc/companies — Webflow company rows: name, category,
description, founders and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.lumir.vc/companies"
PRIMARY = "Lumir Ventures"


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
    for it in s.select(".company_row"):
        nm = txt(it.select_one(".company_row_name"))
        if not nm:
            continue
        cat = txt(it.select_one(".row_cat"))
        a = it if it.name == "a" else it.select_one("a[href]")
        out.append(rec(nm, txt(it.select_one(".company_row_desc")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [],
                       founders=txt(it.select_one(".company_row_founders")), detail_url=urljoin(SOURCE_URL, a["href"]) if a and a.get("href") else None))
    finish(out, "lumir", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
