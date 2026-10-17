#!/usr/bin/env python3
"""Radian Capital portfolio scraper -> radiancapital_companies.json
Source: https://www.radiancapital.com/companies — company pop-ups: name, status, theme and
description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.radiancapital.com/companies"
PRIMARY = "Radian Capital"


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
    for w in s.select("div.companies-popup_item-wrapper"):
        nm = txt(w.select_one("h3"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        st = txt(w.select_one(".text-size-large-company-popup"))
        th = w.select_one(".companies-popup_column-right")
        th = [clean(x) for x in th.stripped_strings][1:] if th else []
        d = txt(w.select_one(".w-richtext"))
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at, status=st, sector=", ".join(th) or None))
    finish(out, "radiancapital", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
