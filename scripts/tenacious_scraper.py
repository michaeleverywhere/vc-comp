#!/usr/bin/env python3
"""Tenacious Ventures portfolio scraper -> tenacious_companies.json
Source: https://tenacious.ventures/investments — Investments list: company name, theme, description and
website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://tenacious.ventures/investments"
PRIMARY = "Tenacious Ventures"


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
    for it in s.select("div.post-wrapper"):
        nm = txt(it.select_one("div.post-title"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in it.stripped_strings if clean(x)]
        i = p.index(nm) if nm in p else 0
        a = [x for x in it.select("a[href^=http]")]
        out.append(rec(nm, p[i + 1] if len(p) > i + 1 else None, site(a[0]) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       theme=p[0] if i > 0 else None))
    finish(out, "tenacious", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
