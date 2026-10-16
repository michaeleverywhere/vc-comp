#!/usr/bin/env python3
"""Golden Seeds portfolio scraper -> goldenseeds_companies.json
Source: https://www.goldenseeds.com/our-companies — portfolio cards (`div.pm-item`):
company name, sector tag, short description and website from the detail modal.
Only the server-rendered first page of the list is captured."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.goldenseeds.com/our-companies"
PRIMARY = "Golden Seeds"


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
    for it in s.select("div.pm-item"):
        nm = txt(it.select_one("h2.pm-title"))
        if not nm:
            continue
        c = it.select_one(".pm-content")
        tags = [txt(a) for a in c.select(".tags-listing a") if txt(a)] if c else []
        modal = it.select_one(".modal")
        web = next((site(a) for a in modal.select("a[href^=http]") if site(a)), None) if modal else None
        out.append(rec(nm, txt(c.select_one(".textbox")) if c else None, web, PRIMARY, SOURCE_URL, scraped_at, sectors=tags))
    finish(out, "goldenseeds", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
