#!/usr/bin/env python3
"""Movens Capital portfolio scraper -> movens_companies.json
Source: https://movenscapital.com/our-portfolio/ — Portfolio accordion: company name, one-line
description, sector, entry date, fund and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://movenscapital.com/our-portfolio/"
PRIMARY = "Movens Capital"


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
    for li in s.select("li.portfolio-item"):
        nm = txt(li.select_one("h3.portfolio-title"))
        if not nm:
            continue
        try:
            funds = json.loads(li.get("data-filters") or "[]")
        except ValueError:
            funds = []
        sec = txt(li.select_one(".sector-label"))
        a = li.select_one("a.website-link-wrapper[href]")
        out.append(rec(nm, txt(li.select_one("p.summary-desc")), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sec] if sec else [], entry_date=txt(li.select_one(".date-label")), fund=", ".join(funds) or None))
    finish(out, "movens", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
