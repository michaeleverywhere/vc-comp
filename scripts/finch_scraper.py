#!/usr/bin/env python3
"""Finch Capital portfolio scraper -> finch_companies.json
Source: https://finchcapital.com/portfolio — Portfolio cards: company name, description,
headquarters and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://finchcapital.com/portfolio"
PRIMARY = "Finch Capital"


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
    for h in s.select("h3.type-h3"):
        box = h.find_parent("div", class_="h-full") or h.parent
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in box.stripped_strings if clean(x)]
        hq = p[p.index("Headquarters:") + 1] if "Headquarters:" in p[:-1] else None
        a = box.select_one("a[href^=http]")
        out.append(rec(nm, p[1] if len(p) > 1 and p[1] != "Headquarters:" else None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       location=hq))
    finish(out, "finch", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
