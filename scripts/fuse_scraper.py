#!/usr/bin/env python3
"""Fuse portfolio scraper -> fuse_companies.json
Source: https://fuse.vc/investments — Investments list: company name, category and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://fuse.vc/investments"
PRIMARY = "Fuse"


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
    for li in s.select("li.v2-rule"):
        a = li.select_one("a[href]")
        sp = [txt(x) for x in li.select("a > span")]
        nm = sp[0] if sp else None
        if not nm:
            continue
        cat = txt(li.select_one(".v2-label"))
        out.append(rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else []))
    finish(out, "fuse", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
