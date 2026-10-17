#!/usr/bin/env python3
"""Array Ventures portfolio scraper -> arrayvc_companies.json
Source: https://www.array.vc/portfolio — Astro portfolio tiles: company name, sector and
stage label, description, latest-news date/headline and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.array.vc/portfolio"
PRIMARY = "Array Ventures"


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
    for a in s.select("a.tile.group"):
        sp = a.find_all("span", recursive=False)
        nm = txt(sp[1]) if len(sp) > 1 else None
        if not nm:
            continue
        lab = txt(sp[2]) if len(sp) > 2 else None
        sec, stg = None, None
        if lab:
            parts = [clean(x) for x in lab.split("·")]
            sec = parts[0] or None
            stg = parts[1] if len(parts) > 1 else None
        rv = a.select_one("span.reveal")
        rs = rv.find_all("span", recursive=False) if rv else []
        out.append(rec(nm, txt(rs[1]) if len(rs) > 1 else None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [],
                       stage=stg, latest_news_date=txt(rs[2]) if len(rs) > 2 else None,
                       latest_news=txt(rs[3]) if len(rs) > 3 else None, detail_url=urljoin(SOURCE_URL, a["href"])))
    finish(out, "arrayvc", ("description", "stage", "everywhere_tags"))


if __name__ == "__main__":
    main()
