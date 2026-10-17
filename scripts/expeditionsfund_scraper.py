#!/usr/bin/env python3
"""Expeditions Fund portfolio scraper -> expeditionsfund_companies.json
Source: https://www.expeditionsfund.com/portfolio — portfolio grid: company name, website and
'Acquired' label (shown only when set)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.expeditionsfund.com/portfolio"
PRIMARY = "Expeditions Fund"


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
    for a in s.select("a.portfolio-item"):
        info = a.select_one(".portfolio-info-w")
        if not info:
            continue
        ss = [clean(x) for x in info.stripped_strings if clean(x)]
        if not ss:
            continue
        nm = ss[0]
        if nm.lower() in seen:
            continue
        seen.add(nm.lower())
        acq = "Acquired" in ss[1:]
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, status="exited" if acq else None))
    finish(out, "expeditionsfund", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
