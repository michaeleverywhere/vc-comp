#!/usr/bin/env python3
"""Syncona portfolio scraper -> syncona_companies.json
Source: https://www.synconaltd.com/portfolio/ — Portfolio list: company name, description and stage
category (from the company page path)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.synconaltd.com/portfolio/"
PRIMARY = "Syncona"


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
    for h in s.select("h3"):
        box = h.parent
        a = box.select_one("a[href*='/portfolio/']")
        if not a or a.get("href", "").rstrip("/").count("/") < 3:
            continue
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in box.stripped_strings if clean(x)]
        cat = a["href"].strip("/").split("/")[-2].replace("-", " ")
        out.append(rec(nm, p[1] if len(p) > 1 else None, None, PRIMARY, SOURCE_URL, scraped_at, stage=cat))
    finish(out, "syncona", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
