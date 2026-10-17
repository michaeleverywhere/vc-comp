#!/usr/bin/env python3
"""Scout Ventures portfolio scraper -> scout_companies.json
Source: https://www.scout.vc/companies — Webflow companies list: name, short
description, industry, fund, exit flag, long description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.scout.vc/companies"
PRIMARY = "Scout Ventures"


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
    for it in s.select("div.companies-list-item"):
        nm = txt(it.select_one(".company_name-list-view")) or txt(it.select_one("h2"))
        if not nm:
            continue
        ind = txt(it.select_one(".company-industry"))
        fund = txt(it.select_one("[fs-cmsfilter-field='fund']"))
        ex = (txt(it.select_one("[fs-cmsfilter-field='exitstatus']")) or "").lower() == "true"
        long_d = txt(it.select_one(".rtb-companies"))
        web = next((a for a in it.select(".companies-list-item-body-copy a[href^='http']") if site(a)), None)
        out.append(rec(nm, long_d or txt(it.select_one(".company-short-description")), site(web), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[ind] if ind else [], tagline=txt(it.select_one(".company-short-description")), fund=fund,
                       status="exited" if ex else None, detail_url=urljoin(SOURCE_URL, it.select_one("a.anchor-link")["href"]) if it.select_one("a.anchor-link") else None))
    finish(out, "scout", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
