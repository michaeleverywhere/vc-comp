#!/usr/bin/env python3
"""Coalition Operators portfolio scraper -> coalition_companies.json
Source: https://www.coalitionoperators.com/portfolio — Webflow CMS portfolio
popups: company name, description, year invested, industry tags and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.coalitionoperators.com/portfolio"
PRIMARY = "Coalition Operators"


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
    for it in s.select("div.portfolio-list-item-wrapper.w-dyn-item"):
        nm = txt(it.select_one(".portfolio-company-name"))
        if not nm:
            continue
        tags = [txt(x) for x in it.select("[fs-cmsfilter-field='industry']") if txt(x)]
        out.append(rec(nm, txt(it.select_one(".portfolio-company-description-2")), site(it.select_one("a.portfolio-link")), PRIMARY,
                       SOURCE_URL, scraped_at, sectors=tags, year_invested=year_of(txt(it.select_one(".portfolio-invited-cnt-2 p.paragraph")))))
    finish(out, "coalition", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
