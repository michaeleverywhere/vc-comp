#!/usr/bin/env python3
"""Kaya Ventures portfolio scraper -> kaya_companies.json
Source: https://www.kaya.vc/portfolio — portfolio list rows: company name, one-line
description, status pill (e.g. Exited / RIP) and website when linked."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.kaya.vc/portfolio"
PRIMARY = "Kaya Ventures"


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
    for li in s.select("li.group"):
        nm = txt(li.select_one("span.font-serif"))
        if not nm:
            continue
        pill = txt(li.select_one("span.rounded-full"))
        a = li.select_one("a[href]")
        out.append(rec(nm, txt(li.select_one("span.font-sans")), site(a), PRIMARY, SOURCE_URL, scraped_at, portfolio_status=pill,
                       status="exited" if pill and "exit" in pill.lower() else ("closed" if pill and pill.upper() == "RIP" else None)))
    finish(out, "kaya", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
