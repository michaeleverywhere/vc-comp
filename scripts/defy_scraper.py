#!/usr/bin/env python3
"""Defy Partners portfolio scraper -> defy_companies.json
Source: https://defy.vc/companies/ — Companies list: company name and description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://defy.vc/companies/"
PRIMARY = "Defy Partners"


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
    for t in s.select("div.company_title"):
        a = t.find_parent("a") or t.parent
        nm = txt(t)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in a.stripped_strings if clean(x)]
        d = [x for x in p if x != nm]
        out.append(rec(nm, d[-1] if d else None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "defy", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
