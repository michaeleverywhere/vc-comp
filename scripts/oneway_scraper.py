#!/usr/bin/env python3
"""One Way Ventures portfolio scraper -> oneway_companies.json
Source: https://www.onewayvc.com/portfolio — Webflow portfolio table: company name, one-line
description, category, investment stage, year partnered, status label and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.onewayvc.com/portfolio"
PRIMARY = "One Way Ventures"


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
    for a in s.select("a.link-table[href]"):
        nm = txt(a.select_one("[fs-cmssort-field=name]"))
        if not nm:
            continue
        lab = txt(a.select_one(".lable-block-grid"))
        cat = txt(a.select_one(".table-data.category"))
        out.append(rec(nm, txt(a.select_one(".text-block-6")), None, PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [],
                       stage=txt(a.select_one(".table-data.investment")), partnered_year=txt(a.select_one(".year")), portfolio_status=lab,
                       status="exited" if lab and re.search(r"acqui|exit|ipo", lab, re.I) else None, detail_url=urljoin(SOURCE_URL, a["href"])))
    finish(out, "oneway", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
