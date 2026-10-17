#!/usr/bin/env python3
"""Puzzle Ventures portfolio scraper -> puzzleventures_companies.json
Source: https://www.puzzle.ventures/portfolio/ — portfolio list: project name, sector
and one-line description, website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.puzzle.ventures/portfolio/"
PRIMARY = "Puzzle Ventures"


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
    for h in s.select("h3"):
        nm = txt(h)
        row = h.find_parent("div", class_="border-b-2")
        if not nm or row is None or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in row.stripped_strings if clean(x) and clean(x) != nm]
        a = row.find_parent("a") or row.select_one("a[href^=http]")
        out.append(rec(nm, ss[1] if len(ss) > 1 else None, site(a), PRIMARY, SOURCE_URL, scraped_at, sectors=[ss[0]] if ss else []))
    finish(out, "puzzleventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
