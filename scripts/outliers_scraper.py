#!/usr/bin/env python3
"""Outliers VC portfolio scraper -> outliers_companies.json
Source: https://outliers.vc/portfolio — Portfolio accordion: company name, country, theme and
website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://outliers.vc/portfolio"
PRIMARY = "Outliers VC"


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
    for it in s.select("div.accordion-item.investment"):
        h = it.select_one("h2")
        p = [clean(x) for x in (h.stripped_strings if h else [])]
        if not p or p[0].lower() in seen:
            continue
        seen.add(p[0].lower())
        loc = p[1].strip("()") if len(p) > 1 else None
        th = p[2].strip("()") if len(p) > 2 else None
        a = [x for x in it.select("a[href^=http]") if "linkedin.com" not in x["href"]]
        out.append(rec(p[0], None, site(a[-1]) if a else None, PRIMARY, SOURCE_URL, scraped_at, location=loc, theme=th))
    finish(out, "outliers", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
