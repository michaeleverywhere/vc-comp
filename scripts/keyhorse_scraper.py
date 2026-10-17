#!/usr/bin/env python3
"""Keyhorse Capital portfolio scraper -> keyhorse_companies.json
Source: https://www.keyhorse.vc/portfolio — portfolio table: company name, sector,
classification (Direct / Programmatic) and exit flag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.keyhorse.vc/portfolio"
PRIMARY = "Keyhorse Capital"


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
    for b in s.select("button.pf-row"):
        n = b.select_one(".pf-name")
        if n is None:
            continue
        ex = n.select_one(".pf-exit")
        if ex is not None:
            ex.extract()
        nm = txt(n)
        if not nm:
            continue
        sec = txt(b.select_one(".pf-row-value:not(.pf-row-classification)"))
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec and sec != "Untagged" else [],
                       investment_type=txt(b.select_one(".pf-classification")), status="exited" if ex is not None else None))
    finish(out, "keyhorse", ("everywhere_tags",))


if __name__ == "__main__":
    main()
