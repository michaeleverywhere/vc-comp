#!/usr/bin/env python3
"""Lightbank portfolio scraper -> lightbank_companies.json
Source: https://www.lightbank.com/companies — 'Our Companies' list: company name (one
paragraph per company in the site's text block; links where present)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.lightbank.com/companies"
PRIMARY = "Lightbank"


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
    blocks = [d for d in s.select("div.sqs-html-content") if len(d.find_all("p")) >= 10]
    for p in [p for d in blocks for p in d.find_all("p")]:
        nm = clean(p.get_text(" ", strip=True))
        if not nm or nm.lower() in seen or len(nm) > 45:
            continue
        seen.add(nm.lower())
        a = p.find("a", href=re.compile(r"^https?://"))
        out.append(rec(nm.replace("®", "").strip(), None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "lightbank", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
