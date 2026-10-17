#!/usr/bin/env python3
"""Flux Capital portfolio scraper -> fluxcapital_companies.json
Source: https://www.fluxcapital.com/portfolio — Portfolio list: company name, stage(s) invested
and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.fluxcapital.com/portfolio"
PRIMARY = "Flux Capital"


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
    for a in s.select("a[href^=http]"):
        p = [clean(x) for x in a.stripped_strings if clean(x)]
        if len(p) < 2 or not re.fullmatch(r"\d{2}", p[0]) or p[1].lower() in seen:
            continue
        seen.add(p[1].lower())
        out.append(rec(p[1], None, site(a), PRIMARY, SOURCE_URL, scraped_at, stage=p[2] if len(p) > 2 else None))
    finish(out, "fluxcapital", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
