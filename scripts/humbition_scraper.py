#!/usr/bin/env python3
"""Humbition portfolio scraper -> humbition_companies.json
Source: https://humbition.com/portfolio/ — numbered portfolio list: company name with
website link, description and founder name(s)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://humbition.com/portfolio/"
PRIMARY = "Humbition"


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
    for li in s.select("ol > li"):
        a = li.select_one("h2 a") or li.select_one("h2")
        nm = txt(a)
        if not nm:
            continue
        ps = [p for p in li.select("p") if txt(p)]
        desc = txt(ps[0]) if ps else None
        founders = [txt(x) for x in li.select("p a") if txt(x) and "linkedin" in (x.get("href") or "")]
        out.append(rec(nm, desc, site(a) if a and a.name == "a" else None, PRIMARY, SOURCE_URL, scraped_at, founders=founders))
    finish(out, "humbition", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
