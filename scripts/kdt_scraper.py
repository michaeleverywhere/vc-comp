#!/usr/bin/env python3
"""KdT Ventures portfolio scraper -> kdt_companies.json
Source: https://www.kdtvc.com/portfolio — Portfolio table: company name, sector, stage and
website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.kdtvc.com/portfolio"
PRIMARY = "KdT Ventures"


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
    for li in s.select("li[class*=PortfolioTable_rowItem]"):
        nm = clean(" ".join(li.select_one("[class*=PortfolioTable_rowName]").stripped_strings)) if li.select_one("[class*=PortfolioTable_rowName]") else None
        if not nm:
            continue
        a = li.select_one("a[href^=http]")
        sec = txt(li.select_one("[class*=PortfolioTable_rowSector]"))
        stage = clean("".join(x.get_text() for x in li.select("[class*=PortfolioTable_rowStage] span"))) or txt(li.select_one("[class*=PortfolioTable_rowStage]"))
        out.append(rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [], stage=stage))
    finish(out, "kdt", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
