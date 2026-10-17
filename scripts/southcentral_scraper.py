#!/usr/bin/env python3
"""South Central Ventures portfolio scraper -> southcentral_companies.json
Source: https://sc-ventures.com/portfolio/ — portfolio grid: company name (logo alt
text), website, one-line description and sector."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://sc-ventures.com/portfolio/"
PRIMARY = "South Central Ventures"


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
    for it in s.select(".element-item"):
        a = it.select_one(".portfolio-img a")
        img = it.select_one("img")
        nm = clean(img.get("alt")) if img else None
        if not nm:
            continue
        out.append(rec(nm, txt(it.select_one("p")), site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[txt(x) for x in it.select("li") if txt(x)]))
    finish(out, "southcentral", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
