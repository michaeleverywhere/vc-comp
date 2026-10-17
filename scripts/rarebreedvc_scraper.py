#!/usr/bin/env python3
"""Rarebreed Ventures portfolio scraper -> rarebreedvc_companies.json
Source: https://www.rarebreed.vc/companies — companies page: company name (h2 link text)
and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.rarebreed.vc/companies"
PRIMARY = "Rarebreed Ventures"


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
    for h in s.select("h2"):
        a = h.find("a", href=re.compile(r"^https?://"))
        nm = clean(h.get_text(" ", strip=True).replace("\u200d", "").replace("\xa0", " "))
        if not nm or nm.lower() in seen or len(nm) > 40:
            continue
        seen.add(nm.lower())
        out.append(rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "rarebreedvc", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
