#!/usr/bin/env python3
"""Qbic portfolio scraper -> qbic_companies.json
Source: https://qbic.be/portfolio — Portfolio list: company name, fund, sector and
description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://qbic.be/portfolio"
PRIMARY = "Qbic"


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
    for h in s.select("h3.portfolio-heading"):
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        box = h.find_parent(class_="portfolio-content-wrapper") or h.parent
        p = [clean(x) for x in box.stripped_strings if clean(x)]
        i = p.index(nm) if nm in p else -1
        fund = p[0] if p and p[0].lower().startswith("qbic") else None
        sec = next((x for x in p[1:i] if not x.isdigit() and x != fund), None) if i > 1 else None
        out.append(rec(nm, p[i + 1] if i >= 0 and len(p) > i + 1 else None, None, PRIMARY, SOURCE_URL, scraped_at, fund=fund,
                       sectors=[sec] if sec else []))
    finish(out, "qbic", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
