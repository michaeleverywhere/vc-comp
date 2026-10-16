#!/usr/bin/env python3
"""Pathlight Ventures portfolio scraper -> pathlight_companies.json
Source: https://pathlight.vc/portfolio — portfolio list rows: company name,
description, Pathlight theme and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://pathlight.vc/portfolio"
PRIMARY = "Pathlight Ventures"


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
    for a in s.select("a.grid.grid-cols-1"):
        d = a.find_all("div", recursive=False)
        nm = txt(d[0]) if d else None
        if not nm:
            continue
        th = txt(d[2]) if len(d) > 2 else None
        out.append(rec(nm, txt(d[1]) if len(d) > 1 else None, site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[th] if th else []))
    finish(out, "pathlight", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
