#!/usr/bin/env python3
"""Ocean Azul Partners portfolio scraper -> oceanazul_companies.json
Source: https://oceanazulpartners.com/portfolio/ — Portfolio blurbs: company name, website and
one-line description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://oceanazulpartners.com/portfolio/"
PRIMARY = "Ocean Azul Partners"


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
    for b in s.select("div.et_pb_blurb_content"):
        h = b.select_one("h4.et_pb_module_header")
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        a = b.select_one("a[href^=http]")
        out.append(rec(nm, txt(b.select_one(".et_pb_blurb_description")), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "oceanazul", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
