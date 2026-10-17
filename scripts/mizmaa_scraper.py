#!/usr/bin/env python3
"""MizMaa Ventures portfolio scraper -> mizmaa_companies.json
Source: https://www.mizmaa.com/portfolio — Portfolio cards: company name, tagline, sector and
exited flag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.mizmaa.com/portfolio"
PRIMARY = "MizMaa Ventures"


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
    for c in s.select("div.portfolio-card"):
        nm = txt(c.select_one("div.name-caption"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in c.stripped_strings if clean(x) and clean(x) != nm]
        ex = bool(p) and p[0].lower() == "exited"
        if ex:
            p = p[1:]
        out.append(rec(nm, p[0] if p else None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=p[1:2],
                       status="exited" if ex else None))
    finish(out, "mizmaa", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
