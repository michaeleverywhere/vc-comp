#!/usr/bin/env python3
"""Bungalow portfolio scraper -> bungalow_companies.json
Source: https://www.bungalow.vc/ — homepage portfolio list: company name (link text)
and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.bungalow.vc/"
PRIMARY = "Bungalow"


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
    for a in s.select("a[href^='http']"):
        if "bungalow" in a["href"] or re.search(r"linkedin|twitter|x\.com|instagram|framer", a["href"]):
            continue
        nm = txt(a)
        if not nm or nm.lower() in seen or len(nm.split()) > 4:
            continue
        seen.add(nm.lower())
        out.append(rec(nm, None, a["href"], PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "bungalow", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
