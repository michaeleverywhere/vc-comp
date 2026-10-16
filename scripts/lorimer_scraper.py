#!/usr/bin/env python3
"""Lorimer Ventures portfolio scraper -> lorimer_companies.json
Source: https://www.lorimerventures.com/portfolio — Webflow CMS portfolio cards:
company name, category, location, description (when filled) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.lorimerventures.com/portfolio"
PRIMARY = "Lorimer Ventures"


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
    for it in s.select("div.coll-item-logos-portfolio.w-dyn-item"):
        box = it.select_one(".wp-name-and-category-portfolio")
        nm = txt(box.select_one(".custom-title-name-portfolio")) if box else None
        if not nm:
            continue
        cat = [txt(d) for d in box.find_all("div", recursive=False) if not d.get("class") and txt(d)]
        d = it.select_one("p.custom-description-item-portfolio")
        d = txt(d) if d and "w-dyn-bind-empty" not in (d.get("class") or []) else None
        out.append(rec(nm, d, site(it.select_one("a.button-link-portfolio")), PRIMARY, SOURCE_URL, scraped_at, sectors=cat,
                       location=txt(it.select_one(".custom-text-location-card"))))
    finish(out, "lorimer", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
