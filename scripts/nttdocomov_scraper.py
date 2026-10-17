#!/usr/bin/env python3
"""NTT Docomo Ventures portfolio scraper -> nttdocomov_companies.json
Source: https://www.nttdocomo-v.com/en/portfolio/ — English portfolio list
(`section.pList li`): company name (site-authored logo alt), profile link, region,
categories, investment year and exit flag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.nttdocomo-v.com/en/portfolio/"
PRIMARY = "NTT Docomo Ventures"


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
    for li in s.select("section.pList li"):
        img = li.find("img", alt=True)
        nm = clean(img.get("alt")) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        a = li.find("a", href=True)
        etc = clean(li.get("data-etc")) or None
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, profile_url=a["href"] if a else None,
                       region=clean(li.get("data-area")) or None, categories=clean(li.get("data-category")) or None,
                       year=year_of(li.get("data-year") or ""), exit_note=etc))
    finish(out, "nttdocomov", ("everywhere_tags",))


if __name__ == "__main__":
    main()
