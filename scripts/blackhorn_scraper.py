#!/usr/bin/env python3
"""Blackhorn Ventures portfolio scraper -> blackhorn_companies.json
Source: https://www.blackhornvc.com/portfolio — Webflow CMS company rows: name,
short description, industry, fund vintage and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.blackhornvc.com/portfolio"
PRIMARY = "Blackhorn Ventures"


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
    for r in s.select("div.company-row"):
        nm = txt(r.select_one(".txt-32px-bold"))
        if not nm:
            continue
        ind = [txt(x) for x in r.select("[fs-cmsfilter-field='industry']") if txt(x)]
        vin = [txt(x) for x in r.select("[fs-cmsfilter-field='vintage']") if txt(x)]
        a = r.select_one("a.rounded-btn")
        out.append(rec(nm, txt(r.select_one(".company-short-description")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=ind,
                       fund=", ".join(vin) or None, detail_url=urljoin(SOURCE_URL, a["href"]) if a and a.get("href") else None))
    finish(out, "blackhorn", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
