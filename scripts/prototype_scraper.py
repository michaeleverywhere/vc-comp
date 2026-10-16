#!/usr/bin/env python3
"""Prototype Capital portfolio scraper -> prototype_companies.json
Source: https://www.prototypecap.com/index.html — portfolio grid: company name, one-line
description, first-check year and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.prototypecap.com/index.html"
PRIMARY = "Prototype Capital"


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
    for c in s.select("div.col-md-4"):
        p = c.select_one("div.d-flex p")
        a = p.find("a") if p else None
        nm = txt(a)
        if not nm:
            continue
        lines = [clean(x) for x in p.stripped_strings if clean(x)]
        d = lines[1] if len(lines) > 1 and "first check" not in lines[1].lower() else None
        fc = next((x for x in lines if "first check" in x.lower()), None)
        out.append(rec(nm, d, site(a), PRIMARY, SOURCE_URL, scraped_at, first_check_year=year_of(fc)))
    finish(out, "prototype", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
