#!/usr/bin/env python3
"""aMoon Fund portfolio scraper -> amoon_companies.json
Source: https://www.amoon.fund/ — homepage portfolio grid (`div.item`): company name
(site-authored logo alt / link title), profile link and listing note (e.g. ticker)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.amoon.fund/"
PRIMARY = "aMoon Fund"


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
    for it in s.select("div.item"):
        a = it.find("a", href=True)
        if not a:
            continue
        nm = clean(a.get("title")) or (clean(it.find("img", alt=True).get("alt")) if it.find("img", alt=True) else None)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        note = txt(it.select_one(".bottom-text"))
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, profile_url=a["href"], listing=note))
    finish(out, "amoon", ("everywhere_tags",))


if __name__ == "__main__":
    main()
