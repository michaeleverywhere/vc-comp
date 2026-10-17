#!/usr/bin/env python3
"""TMV portfolio scraper -> tmv_companies.json
Source: https://www.tmv.vc/companies — investment table: company name, industry (icon label)
and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.tmv.vc/companies"
PRIMARY = "TMV"


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
    for row in s.select("div[class*='InvestmentTableBlock-module'][class$='__row']"):
        nm = txt(row.select_one("[class*='__name']"))
        if not nm:
            continue
        ic = row.select_one("img[class*='__industryIcon']")
        ind = clean(re.sub(r"\s*icon$", "", ic.get("alt") or "", flags=re.I)) if ic else None
        out.append(rec(nm, None, site(row.select_one("a[class*='__websiteButton']")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[ind] if ind else []))
    finish(out, "tmv",  ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
