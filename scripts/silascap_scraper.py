#!/usr/bin/env python3
"""Silas Capital portfolio scraper -> silascap_companies.json
Source: https://silascapital.com/portfolio — portfolio brand tiles (Growth / Venture
Investments): brand name (site-authored alt) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://silascapital.com/portfolio"
PRIMARY = "Silas Capital"


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
    for a in s.select("a.brand-tile"):
        img = a.find("img", alt=True)
        nm = clean(img.get("alt")) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        h = a.find_previous("h3")
        grp = "Growth" if h and "Growth" in txt(h) else ("Venture" if h and "Venture" in txt(h) else None)
        href = a.get("data-href") or ""
        out.append(rec(nm, None, (href if href.startswith("http") else None), PRIMARY, SOURCE_URL, scraped_at, investment_type=grp))
    finish(out, "silascap", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
