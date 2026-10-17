#!/usr/bin/env python3
"""Tera Ventures portfolio scraper -> tera_companies.json
Source: https://www.tera.vc/ — homepage portfolio items: company name, one-line
description, location and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.tera.vc/"
PRIMARY = "Tera Ventures"


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
    for it in s.select(".port-item"):
        c = it.select_one(".content")
        nm = txt(c.find("strong")) if c else None
        if not nm:
            continue
        divs = c.find_all("div", recursive=False)
        loc = None
        if len(divs) > 1:
            loc = clean("".join(t for t in divs[1].find_all(string=True, recursive=False)))
        out.append(rec(nm, txt(c.find("p")), site(c.select_one("a[href^='http']")), PRIMARY, SOURCE_URL, scraped_at, location=loc))
    finish(out, "tera", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
