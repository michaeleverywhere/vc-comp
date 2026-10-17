#!/usr/bin/env python3
"""Mouro Capital portfolio scraper -> mouro_companies.json
Source: https://www.mourocapital.com/our-portfolio/ — Portfolio grid: company name, description, website
and exit tag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.mourocapital.com/our-portfolio/"
PRIMARY = "Mouro Capital"


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
    for it in s.select("div.portfolio-grid__intro"):
        nm = txt(it.select_one("h6"))
        if not nm:
            continue
        box = it.parent
        ex = box.select_one(".exit_tag") if box else None
        a = it.select_one("a.portfolio-grid__link[href]")
        out.append(rec(nm, txt(it.select_one(".portfolio-grid__text")), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       status="exited" if ex and txt(ex) else None))
    finish(out, "mouro", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
