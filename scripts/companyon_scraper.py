#!/usr/bin/env python3
"""Companyon Ventures portfolio scraper -> companyon_companies.json
Source: https://companyon.vc/portfolio/ — founder cards (image alt
'<founder> | <company>'): company name and founders."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://companyon.vc/portfolio/"
PRIMARY = "Companyon Ventures"


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
    founders = {}
    for f in s.select("div.founder"):
        img = f.find("img")
        alt = img.get("alt") if img else ""
        if "|" not in (alt or ""):
            continue
        nm = clean(alt.split("|", 1)[1])
        who = txt(f.select_one(".name"))
        if nm:
            founders.setdefault(nm, [])
            if who and who not in founders[nm]:
                founders[nm].append(who)
    for nm, who in founders.items():
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, founders=", ".join(who) or None))
    finish(out, "companyon", ("everywhere_tags",))


if __name__ == "__main__":
    main()
