#!/usr/bin/env python3
"""Parameter Ventures portfolio scraper -> parameter_companies.json
Source: https://www.parameter.vc/portfolio — Wix portfolio gallery: company name and
description (image alt 'Name: description') and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.parameter.vc/portfolio"
PRIMARY = "Parameter Ventures"


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
    for img in s.select("img[alt]"):
        alt = img.get("alt") or ""
        if ":" not in alt or alt.startswith("Parameter Ventures"):
            continue
        nm, d = [clean(x) for x in alt.split(":", 1)]
        a = img.find_parent("a")
        out.append(rec(nm, d, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "parameter", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
