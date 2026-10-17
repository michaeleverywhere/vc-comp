#!/usr/bin/env python3
"""Cutting Horse portfolio scraper -> cuttinghorse_companies.json
Source: https://www.cuttinghorse.com/portfolio — portfolio cards: company name, category and
status (Active / Exited)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.cuttinghorse.com/portfolio"
PRIMARY = "Cutting Horse"


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
    for b in s.select(".portfolio-card"):
        nm = txt(b.select_one(".portfolio-card-bottom strong"))
        if not nm:
            continue
        cat = txt(b.select_one(".portfolio-card-bottom small"))
        st = txt(b.select_one(".portfolio-card-top"))
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [], portfolio_status=st,
                       status=st.lower() if st else None))
    finish(out, "cuttinghorse", ("everywhere_tags",))


if __name__ == "__main__":
    main()
