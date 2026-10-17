#!/usr/bin/env python3
"""Alpha JWC Ventures portfolio scraper -> alphajwc_companies.json
Source: https://www.alphajwc.com/portfolios/ — Portfolio cards: company name, description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.alphajwc.com/portfolios/"
PRIMARY = "Alpha JWC Ventures"


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
    for a in s.select("a.ajwc-portfolio-card"):
        nm = txt(a.select_one("h3")) or clean((a.select_one("img[alt]") or {}).get("alt") or "")
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        d = txt(a.select_one("p"))
        d = d.replace("\u00c2\u00ae", "\u00ae").replace("\u00c2\u00a0", " ") if d else d
        out.append(rec(nm, d, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "alphajwc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
