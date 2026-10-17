#!/usr/bin/env python3
"""Hilltop Venture Partners portfolio scraper -> hilltop_companies.json
Source: https://hilltopventurepartners.com/portfolio/ — Divi portfolio blurbs: company name,
short description, status and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://hilltopventurepartners.com/portfolio/"
PRIMARY = "Hilltop Venture Partners"


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


def hstat(st):
    t = (st or "").lower()
    if t.startswith("bought by") or "acqui" in t:
        return "acquired"
    if t == "ipo":
        return "public"
    if t in ("died", "closed", "shut down"):
        return "closed"
    return None


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for c in s.select("div.et_pb_column_1_4"):
        a = c.select_one("h4.et_pb_module_header a")
        nm = txt(a)
        if not nm:
            continue
        st = txt(c.select_one(".et_pb_text_inner"))
        out.append(rec(nm, txt(c.select_one(".et_pb_blurb_description")), None, PRIMARY, SOURCE_URL, scraped_at, portfolio_status=st,
                       status=hstat(st), detail_url=a.get("href")))
    finish(out, "hilltop", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
