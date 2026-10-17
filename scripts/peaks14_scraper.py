#!/usr/bin/env python3
"""14 Peaks Capital portfolio scraper -> peaks14_companies.json
Source: https://www.14peaks.capital/portfolio — Portfolio flip cards: company name, sector,
description, stage, country, year and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.14peaks.capital/portfolio"
PRIMARY = "14 Peaks Capital"


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
    for it in s.select("div.flip-scene"):
        nm = txt(it.select_one("h2"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in it.stripped_strings if clean(x) and not clean(x).startswith("Visit")]
        i = p.index(nm, 1) if nm in p[1:] else (1 if len(p) > 1 else 0)
        sec = p[i - 1] if i >= 1 and p[i - 1] != nm else None
        rest = p[i + 1:]
        a = it.select_one("a[href^=http]")
        out.append(rec(nm, rest[0] if rest else None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sec] if sec else [], stage=rest[1] if len(rest) > 1 else None,
                       location=rest[2] if len(rest) > 2 else None, year=rest[3] if len(rest) > 3 else None))
    finish(out, "peaks14", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
