#!/usr/bin/env python3
"""Footwork portfolio scraper -> footwork_companies.json
Source: https://footwork.vc/ — homepage 'Who we are' paragraph: named portfolio
companies, each linked to the company site or Footwork's investment post on
nbt.substack.com."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://footwork.vc/"
PRIMARY = "Footwork"


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
    for p in s.select("div.about p"):
        if "invested in" not in (txt(p) or ""):
            continue
        for a in p.find_all("a"):
            nm, h = txt(a), (a.get("href") or "").strip()
            if not nm or nm.lower() in seen:
                continue
            seen.add(nm.lower())
            post = h if "nbt.substack.com/p/" in h else None
            out.append(rec(nm, None, None if post else site(a), PRIMARY, SOURCE_URL, scraped_at, detail_url=post))
    finish(out, "footwork", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
