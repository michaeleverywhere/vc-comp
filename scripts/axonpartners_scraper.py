#!/usr/bin/env python3
"""Axon Partners Group portfolio scraper -> axonpartners_companies.json
Source: https://axonpartnersgroup.com/portfolio/ — portfolio company grid
(`div.blog-post`): company name, one-line description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://axonpartnersgroup.com/portfolio/"
PRIMARY = "Axon Partners Group"


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
    for it in s.select("div.blog-post"):
        nm = txt(it.select_one("h4"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in it.stripped_strings if clean(x) and clean(x) != nm]
        out.append(rec(nm, ss[0] if ss else None, site(it.select_one("a[href^=http]")), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "axonpartners", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
