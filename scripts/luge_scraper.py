#!/usr/bin/env python3
"""Luge Capital portfolio scraper -> luge_companies.json
Source: https://www.luge.vc/portfolio/ — Divi portfolio blocks: company name and tagline."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.luge.vc/portfolio/"
PRIMARY = "Luge Capital"


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
    for h in s.select("div.et_pb_text h3"):
        box = h.find_parent("div", class_="et_pb_text")
        p = [clean(x) for x in box.stripped_strings if clean(x)]
        nm = txt(h)
        if not nm or nm.lower() in seen or "Learn more" not in p or nm.startswith(("\u201c", '"')):
            continue
        seen.add(nm.lower())
        d = [x for x in p if x not in (nm, "Learn more")]
        out.append(rec(nm, d[0] if d else None, None, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "luge", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
