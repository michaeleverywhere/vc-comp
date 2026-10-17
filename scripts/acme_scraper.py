#!/usr/bin/env python3
"""Acme Capital portfolio scraper -> acme_companies.json
Source: https://www.acme.vc/highlighted-portfolio — Framer portfolio cards: company name, description and
website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.acme.vc/highlighted-portfolio"
PRIMARY = "Acme Capital"


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
    for h in s.select("h5"):
        box = h
        for _ in range(5):
            box = box.parent if box.parent else box
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        p = [clean(x) for x in box.stripped_strings if clean(x)]
        if "View Company" not in p:
            continue
        seen.add(nm.lower())
        d = [x for x in p if x != nm and x != "View Company"]
        a = box.select_one("a[href^=http]")
        out.append(rec(nm, d[0] if d else None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "acme", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
