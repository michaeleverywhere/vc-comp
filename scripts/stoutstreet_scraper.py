#!/usr/bin/env python3
"""Stout Street Capital portfolio scraper -> stoutstreet_companies.json
Source: https://www.stoutstreetcapital.com/ — homepage 'portfolio, by fund' lists
(`div.pf-group`): company name, website, Stout Street fund and current/past
heading."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.stoutstreetcapital.com/"
PRIMARY = "Stout Street Capital"


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
    for g in s.select("div.pf-group"):
        fund = txt(g.select_one(".gh .gt"))
        st = txt(g.select_one(".gh .caps"))
        for a in g.select(".pf-list a[href]"):
            nm = txt(a)
            if not nm or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, fund=fund, holding=st))
    finish(out, "stoutstreet", ("company_url", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
