#!/usr/bin/env python3
"""Bon Angels Venture Partners portfolio scraper -> bonangels_companies.json
Source: https://www.bonangels.net/portfolio — Wix portfolio list (Korean): company name, Korean
description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.bonangels.net/portfolio"
PRIMARY = "Bon Angels Venture Partners"


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
    hs = [clean(h.get_text(" ", strip=True)) for h in s.select("h2.font_2")]
    hs = [h for h in hs if h]
    for i, h in enumerate(hs):
        if not h.startswith("http") or i < 2:
            continue
        nm, d = hs[i - 2], hs[i - 1]
        if nm.startswith("http") or d.startswith("http") or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        out.append(rec(nm, d, h, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "bonangels", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
