#!/usr/bin/env python3
"""Seven Stars portfolio scraper -> sevenstars_companies.json
Source: https://www.sevenstars.vc/ — Homepage companies grid: company name, one-line
description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.sevenstars.vc/"
PRIMARY = "Seven Stars"


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
    for n in s.select("div.name"):
        nm = txt(n)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        a = n.find_parent("a")
        box = a or n.parent
        p = [clean(x) for x in box.stripped_strings if clean(x) and clean(x) != nm and len(clean(x)) > 1]
        u = a["href"] if a is not None and a.get("href", "").startswith("http") else None
        out.append(rec(nm, p[0] if p else None, u, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "sevenstars", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
