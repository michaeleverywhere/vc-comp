#!/usr/bin/env python3
"""Martin Ventures portfolio scraper -> martinvc_companies.json
Source: https://www.martinventures.com/portfolio — portfolio (Active Portfolio / Exits): company
name (link text) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.martinventures.com/portfolio"
PRIMARY = "Martin Ventures"


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
        nm = clean(a.get_text(" ", strip=True))
        if not nm or "martinventures" in a["href"] or nm.lower() in seen or len(nm) > 40 or re.search(r"(?i)linkedin|twitter|privacy|login", nm):
            continue
        h = a.find_previous("h2")
        seen.add(nm.lower())
        ex = bool(h and "Exit" in txt(h))
        out.append(rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, status="exited" if ex else None))
    finish(out, "martinvc", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
