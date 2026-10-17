#!/usr/bin/env python3
"""Atinum Investment portfolio scraper -> atinum_companies.json
Source: https://www.atinuminvest.co.kr/portfolio-type — Portfolio modals (Korean): company name, sector,
website and Korean description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.atinuminvest.co.kr/portfolio-type"
PRIMARY = "Atinum Investment"


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
    for h in s.select("h1.company-name"):
        box = h.find_parent(class_="modal-white-bg") or h.parent
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in box.stripped_strings if clean(x) and clean(x) != nm]
        web = next((x for x in p if x.startswith("http")), None)
        rest = [x for x in p if x != web]
        out.append(rec(nm, rest[1] if len(rest) > 1 else None, web, PRIMARY, SOURCE_URL, scraped_at, sectors=rest[:1]))
    finish(out, "atinum", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
