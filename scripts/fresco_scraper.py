#!/usr/bin/env python3
"""Fresco Capital portfolio scraper -> fresco_companies.json
Source: https://fresco.vc/portfolio/ — portfolio flip cards: company name, slogan,
website, region and Fresco sector theme."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://fresco.vc/portfolio/"
PRIMARY = "Fresco Capital"


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
    for it in s.select("div.portfolio-company"):
        nm = txt(it.select_one("span.company-name"))
        if not nm:
            continue
        sec = txt(it.select_one(".sector span"))
        front = txt(it.select_one(".front"))
        out.append(rec(nm, txt(it.select_one("span.company-slogan")), site(it.select_one(".company-info a")), PRIMARY, SOURCE_URL,
                       scraped_at, sectors=[sec] if sec else [], region=txt(it.select_one(".region span")),
                       status="exited" if front and "exit" in front.lower() else None))
    finish(out, "fresco", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
