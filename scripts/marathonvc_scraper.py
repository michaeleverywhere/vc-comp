#!/usr/bin/env python3
"""Marathon Venture Capital portfolio scraper -> marathonvc_companies.json
Source: https://marathon.vc/portfolio — portfolio cells (`.company-cell`):
company name, description, year and profile page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://marathon.vc/portfolio"
PRIMARY = "Marathon Venture Capital"


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
    for it in s.select(".company-cell"):
        nm = txt(it.select_one(".company-cell__name"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        h = it.get("href") if it.name == "a" else None
        out.append(rec(nm, txt(it.select_one(".company-cell__desc")), None, PRIMARY, SOURCE_URL, scraped_at,
                       year_invested=year_of(txt(it.select_one(".company-cell__meta"))), detail_url=urljoin(SOURCE_URL, h) if h else None))
    finish(out, "marathonvc", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
