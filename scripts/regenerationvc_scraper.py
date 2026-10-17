#!/usr/bin/env python3
"""Regeneration.VC portfolio scraper -> regenerationvc_companies.json
Source: https://www.regeneration.vc/portfolio — Portfolio cards: fund, company name, description,
location and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.regeneration.vc/portfolio"
PRIMARY = "Regeneration.VC"


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
    for it in s.select("div.appear-item[data-fund]"):
        p = [clean(x) for x in it.stripped_strings if clean(x) and clean(x) != "View site"]
        fund = p[0] if p else None
        p = p[1:]
        if not p or p[0].lower() in seen:
            continue
        seen.add(p[0].lower())
        a = it.select_one("a[href^=http]")
        out.append(rec(p[0], p[1] if len(p) > 1 else None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, fund=fund,
                       location=p[2] if len(p) > 2 else None, sectors=[it.get("data-theme").title()] if it.get("data-theme") else []))
    finish(out, "regenerationvc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
