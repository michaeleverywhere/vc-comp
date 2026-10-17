#!/usr/bin/env python3
"""1955 Capital portfolio scraper -> capital1955_companies.json
Source: https://1955.capital/portfolio — portfolio image captions: company name,
sector and one-line description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://1955.capital/portfolio"
PRIMARY = "1955 Capital"


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
    for fc in s.select("figcaption"):
        parts = [clean(x) for x in fc.stripped_strings if clean(x)]
        if not parts:
            continue
        nm = parts[0]
        sec = next((p.strip("()") for p in parts[1:] if p.startswith("(") and p.endswith(")")), None)
        desc = next((p for p in parts[1:] if not (p.startswith("(") and p.endswith(")"))), None)
        fig = fc.find_parent("figure")
        a = next((x for x in (fig.select("a[href^='http']") if fig else []) if site(x)), None)
        out.append(rec(nm, desc, site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else []))
    finish(out, "capital1955", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
