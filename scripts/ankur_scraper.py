#!/usr/bin/env python3
"""Ankur Capital portfolio scraper -> ankur_companies.json
Source: https://www.ankurcapital.com/portfolio — Portfolio blocks: company name (site logo alt) and
website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.ankurcapital.com/portfolio"
PRIMARY = "Ankur Capital"


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
    for b in s.select("div.startup-page-block"):
        img = next((i for i in b.select("img[alt]") if (i.get("alt") or "").strip()), None)
        nm = clean(re.sub(r"\s*logo$", "", img.get("alt") or "", flags=re.I)) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in b.stripped_strings if clean(x) and clean(x) != "Text Link"]
        d = next((x for x in p if len(x) > 30), None)
        a = b.select_one("a[href^=http]")
        out.append(rec(nm, d, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "ankur", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
