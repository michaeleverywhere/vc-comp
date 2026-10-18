#!/usr/bin/env python3
"""Delphi Ventures portfolio scraper -> delphiventures_companies.json
Source: https://delphiventures.io/portfolio-crypto — Framer portfolio table: project
name, year invested, sector and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://delphiventures.io/portfolio-crypto"
PRIMARY = "Delphi Ventures"


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
    for h4 in s.select("h4"):
        nm = txt(h4)
        if not nm or nm.lower() in seen:
            continue
        a = h4.find_parent("a")
        row = a or h4.find_parent(class_=re.compile("framer-5bec3e")) or h4.parent.parent.parent
        seen.add(nm.lower())
        yr = txt(row.select_one("p"))
        sec = txt(row.select_one("h6"))
        out.append(rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [], year_invested=year_of(yr)))
    finish(out, "delphiventures", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
