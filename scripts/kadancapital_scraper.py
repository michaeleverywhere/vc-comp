#!/usr/bin/env python3
"""Kadan Capital portfolio scraper -> kadancapital_companies.json
Source: https://kadan.vc/portfolio — Webflow portfolio table: year, company name,
sector, stage, region and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://kadan.vc/portfolio"
PRIMARY = "Kadan Capital"


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
    for a in s.select("a.table-row"):
        cells = [txt(x) for x in a.select(".medium-text")]
        cells = [c for c in cells if c]
        if len(cells) < 2:
            continue
        yr = year_of(cells[0])
        nm = cells[1] if yr else cells[0]
        rest = cells[2:] if yr else cells[1:]
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=rest[:1], stage=rest[1] if len(rest) > 1 else None,
                       region=rest[2] if len(rest) > 2 else None, year=yr, detail_url=urljoin(SOURCE_URL, a.get("href") or "")))
    finish(out, "kadancapital", ("everywhere_tags",))


if __name__ == "__main__":
    main()
