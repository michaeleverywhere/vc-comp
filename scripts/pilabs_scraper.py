#!/usr/bin/env python3
"""Pi Labs portfolio scraper -> pilabs_companies.json
Source: https://pilabs.vc/portfolio — Squarespace portfolio grid: company name, tagline,
founding details and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://pilabs.vc/portfolio"
PRIMARY = "Pi Labs"


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
        nm = txt(it.select_one(".summary-title"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        exc = it.select_one(".summary-excerpt")
        ex = [clean(x) for x in exc.stripped_strings] if exc else []
        web = next((site(a) for a in it.select("a[href^=http]") if site(a)), None)
        out.append(rec(nm, ex[0] if ex else None, web, PRIMARY, SOURCE_URL, scraped_at, details=" ".join(ex[1:]) or None))
    finish(out, "pilabs", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
