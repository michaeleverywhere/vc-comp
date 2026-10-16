#!/usr/bin/env python3
"""Era Ventures portfolio scraper -> era_companies.json
Source: https://eraventures.com/companies/ — expandable company list: company name,
tagline, description, industry buttons and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://eraventures.com/companies/"
PRIMARY = "Era Ventures"


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
    for it in s.select("div.company-item"):
        nm = txt(it.select_one(".type--subhead"))
        if not nm:
            continue
        tag = txt(it.select_one(".type--sm"))
        ind = [txt(x) for x in it.select(".button--secondary") if txt(x)]
        web = next((site(a) for a in it.select("a.button--primary") if site(a)), None)
        out.append(rec(nm, txt(it.select_one(".wysiwyg-content")) or tag, web, PRIMARY, SOURCE_URL, scraped_at, sectors=ind, tagline=tag))
    finish(out, "era", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
