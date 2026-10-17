#!/usr/bin/env python3
"""True Global Ventures portfolio scraper -> trueglobal_companies.json
Source: https://trueglobalventures.com/portfolio — portfolio tiles: company name (logo
caption), description overlay and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://trueglobalventures.com/portfolio"
PRIMARY = "True Global Ventures"


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
    for a in s.select("a.group.bg-card"):
        img = a.find("img")
        cap = a.select_one("div.absolute.bottom-0")
        nm = txt(cap) or (clean(img.get("alt")) if img else None)
        if not nm:
            continue
        ov = a.select_one("div.absolute.inset-0")
        out.append(rec(nm, txt(ov), site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "trueglobal", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
