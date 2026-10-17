#!/usr/bin/env python3
"""Sidecut Ventures portfolio scraper -> sidecut_companies.json
Source: https://sidecut.vc/ — homepage portfolio cards: company name (logo alt),
description and Sidecut's investment note."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://sidecut.vc/"
PRIMARY = "Sidecut Ventures"


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
    for img in s.select("img[alt$=' company logo']"):
        nm = clean(re.sub(r"\s*company logo$", "", img.get("alt") or ""))
        box = img.find_parent("div", class_="relative")
        if not nm or not box:
            continue
        ps = [txt(p) for p in box.select("p") if txt(p)]
        inv = None
        if "Our Investment:" in ps:
            i = ps.index("Our Investment:")
            inv = ps[i + 1] if i + 1 < len(ps) else None
        out.append(rec(nm, ps[0] if ps and ps[0] != "Our Investment:" else None, None, PRIMARY, SOURCE_URL, scraped_at, investment=inv))
    finish(out, "sidecut", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
