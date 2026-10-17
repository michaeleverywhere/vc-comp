#!/usr/bin/env python3
"""OCV Partners portfolio scraper -> ocvpartners_companies.json
Source: https://www.ocvpartners.com/portfolio/ — Divi portfolio grid: company name (h3)
and the site-written description beneath it.
"""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.ocvpartners.com/portfolio/"
PRIMARY = "OCV Partners"



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
    for col in s.select(".et_pb_column.et_pb_column_1_3"):
        h = col.select(".et_pb_text_inner h3")
        if len(h) != 1:
            continue
        nm = txt(h[0])
        ps = [txt(p) for p in col.select(".et_pb_text_inner p") if txt(p)]
        if not ps:
            continue
        out.append(rec(nm, ps[0], None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "ocvpartners", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
