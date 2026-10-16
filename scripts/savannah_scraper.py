#!/usr/bin/env python3
"""Savannah Fund portfolio scraper -> savannah_companies.json
Source: https://savannah.vc/startups — startup cards: company name, country
(upper-case prefix of the excerpt), description and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://savannah.vc/startups"
PRIMARY = "Savannah Fund"


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
    for c in s.select("div.sf-card"):
        a = c.select_one("h2.wp-block-post-title a")
        nm = txt(a)
        if not nm:
            continue
        ex = txt(c.select_one(".wp-block-post-excerpt__excerpt")) or ""
        m = re.match(r"^([A-Z][A-Z .,'&-]+):\s*(.*)$", ex)
        ctry, d = (clean(m.group(1).title()), clean(m.group(2))) if m else (None, ex)
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at, country=ctry, detail_url=a.get("href")))
    finish(out, "savannah", ("description", "country", "everywhere_tags"))


if __name__ == "__main__":
    main()
