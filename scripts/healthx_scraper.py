#!/usr/bin/env python3
"""HealthX Ventures portfolio scraper -> healthx_companies.json
Source: https://www.healthxventures.com/portfolio — Squarespace portfolio text blocks: company
name (h4) and description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.healthxventures.com/portfolio"
PRIMARY = "HealthX Ventures"


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
    for blk in s.select("div.sqs-html-content"):
        h = blk.find("h4")
        p = blk.select_one("p.sqsrte-small") or blk.find("p")
        nm = txt(h)
        if not nm or not p or len(nm) > 60:
            continue
        a = h.find("a") or p.find("a")
        out.append(rec(nm, txt(p), site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "healthx", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
