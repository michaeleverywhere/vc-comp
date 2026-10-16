#!/usr/bin/env python3
"""Foundamental portfolio scraper -> foundamental_companies.json
Source: https://www.foundamental.com/portfolio — Webflow CMS portfolio rows:
company name, stage, year, country, description, sector, market, exit tag,
website and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.foundamental.com/portfolio"
PRIMARY = "Foundamental"


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
    for it in s.select("div.portfolio_item.w-dyn-item"):
        nm = txt(it.select_one("[fs-cmsfilter-field='name']"))
        if not nm:
            continue
        hm = it.select(".hide-mobile-portrait")
        yr = year_of(txt(hm[0])) if hm else None
        ctry = txt(hm[1]) if len(hm) > 1 else None
        tag = txt(it.select_one("[fs-cmsfilter-field='tag']"))
        sec = [txt(x) for x in it.select("[fs-cmsfilter-field='sector']") if txt(x)]
        dl = it.select_one("a.company_page-link")
        out.append(rec(nm, txt(it.select_one(".company_desc")), site(it.select_one("a.external_link")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=sec, stage=txt(it.select_one("[fs-cmsfilter-field='investment-stage']")), year=yr, country=ctry,
                       market=txt(it.select_one("[fs-cmsfilter-field='investment-market']")),
                       status="exited" if tag and "exit" in tag.lower() else None,
                       detail_url=urljoin(SOURCE_URL, dl["href"]) if dl and dl.get("href") else None))
    finish(out, "foundamental", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
