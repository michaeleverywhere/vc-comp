#!/usr/bin/env python3
"""YZR Capital portfolio scraper -> yzr_companies.json
Source: https://yzr-capital.com/portfolio/ — Elementor portfolio blocks: company name, theme and
one-line description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://yzr-capital.com/portfolio/"
PRIMARY = "YZR Capital"


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
    for h in s.select("h3.elementor-heading-title"):
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        box = h
        for _ in range(3):
            box = box.parent
        p = [clean(x) for x in box.stripped_strings if clean(x)]
        if nm not in p:
            continue
        seen.add(nm.lower())
        i = p.index(nm)
        out.append(rec(nm, p[i + 1] if len(p) > i + 1 else None, None, PRIMARY, SOURCE_URL, scraped_at, theme=p[i - 1] if i else None))
    finish(out, "yzr", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
