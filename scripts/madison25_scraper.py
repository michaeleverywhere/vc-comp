#!/usr/bin/env python3
"""25madison portfolio scraper -> madison25_companies.json
Source: https://www.25madison.com/portfolio — portfolio blocks (`a.investments-blocks`):
company name (h5), one-line description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.25madison.com/portfolio"
PRIMARY = "25madison"


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
    # names sit in an h5 Webflow marks w-condition-invisible, which soup_of strips; parse raw HTML here
    s = BeautifulSoup(fetch_response(SOURCE_URL).content.decode("utf-8", "replace"), "html.parser")
    seen = set()
    for a in s.select("a.investments-blocks"):
        nm = txt(a.select_one("h5"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in a.stripped_strings if clean(x)]
        d = next((x for x in ss if x != nm and not x.lower().startswith("visit") and "→" not in x), None)
        out.append(rec(nm, d, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "madison25", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
