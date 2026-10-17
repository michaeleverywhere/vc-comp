#!/usr/bin/env python3
"""Sky9 Capital portfolio scraper -> sky9_companies.json
Source: https://www.sky9.vc/portfolio — Portfolio page (Chinese): company names grouped by
category, with exit/listing markers (stock tickers, acquisition badges)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.sky9.vc/portfolio"
PRIMARY = "Sky9 Capital"


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
    seen = set()
    for i, cat in enumerate(s.select("div.category-content")):
        for it in cat.select("div.company-item"):
            nm = txt(it.select_one(".company-name"))
            if not nm or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            lst = it.select_one(".listing")
            lt = clean(lst.get_text("", strip=True)) if lst else None
            note = "acquired" if lt and "收购" in lt else lt
            out.append(rec(nm, txt(it.select_one(".company-desc")), None, PRIMARY, SOURCE_URL, scraped_at, listing=note,
                           status="exited" if (i == 0 or note) else None))
    finish(out, "sky9", ("everywhere_tags",))


if __name__ == "__main__":
    main()
