#!/usr/bin/env python3
"""Nido Ventures portfolio scraper -> nido_companies.json
Source: https://www.desdeelnido.com/portfolio — Webflow portfolio cards: company name, fund,
sector, year, one-line description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.desdeelnido.com/portfolio"
PRIMARY = "Nido Ventures"


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
    for it in s.select(".portfolio-card"):
        nm = txt(it.select_one("h2.card-title"))
        if not nm:
            continue
        a = it.select_one("a.portfolio-item")
        meta = [txt(x) for x in it.select(".flex-horizontal .text-200") if txt(x)]
        fund = txt(it.select_one(".card-content .z-index-1 .text-200"))
        out.append(rec(nm, txt(it.select_one(".inside-card")), site(a), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[m for m in meta if not re.fullmatch(r"\d{4}", m)], fund=fund,
                       vintage_year=next((m for m in meta if re.fullmatch(r"\d{4}", m)), None)))
    finish(out, "nido", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
