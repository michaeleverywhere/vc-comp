#!/usr/bin/env python3
"""BlueRun Ventures portfolio scraper -> bluerun_companies.json
Source: https://www.brv.com/portfolio — Squarespace portfolio grid: company name and detail
page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.brv.com/portfolio"
PRIMARY = "BlueRun Ventures"


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
    for it in s.select("div.summary-item"):
        a = it.select_one("a.summary-title-link")
        nm = txt(a)
        if not nm:
            img = it.select_one("img[alt]")
            nm = clean(img.get("alt")) if img else None
        if not nm or nm.lower() in seen or re.search(r"\.(png|jpe?g)$", nm, re.I):
            continue
        seen.add(nm.lower())
        h = (a or it.select_one("a[href]")).get("href") if (a or it.select_one("a[href]")) else None
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, detail_url=urljoin(SOURCE_URL, h) if h else None))
    finish(out, "bluerun", ("everywhere_tags",))


if __name__ == "__main__":
    main()
