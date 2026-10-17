#!/usr/bin/env python3
"""Fjor Founders Fund portfolio scraper -> fjor_companies.json
Source: https://www.fjor.co/portfolio — Wix portfolio: company name (h2) and, where
shown, description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.fjor.co/portfolio"
PRIMARY = "Fjor Founders Fund"


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
    for h in s.select("h2.font_2"):
        nm = txt(h)
        if not nm or nm.lower() == "portfolio":
            continue
        box = h
        for _ in range(6):
            box = box.parent
            if box is None or box.select_one("p.font_8"):
                break
        p = box.select_one("p.font_8") if box is not None and len(box.select("h2.font_2")) == 1 else None
        a = h.find("a") or (box.select_one("a[href^='http']") if box is not None and len(box.select("h2.font_2")) == 1 else None)
        out.append(rec(nm, txt(p), site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "fjor", ("everywhere_tags",))


if __name__ == "__main__":
    main()
