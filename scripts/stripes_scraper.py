#!/usr/bin/env python3
"""Stripes portfolio scraper -> stripes_companies.json
Source: https://www.stripes.co/investments — Investment cards: company name, one-line description,
status (Current/Realized) and detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.stripes.co/investments"
PRIMARY = "Stripes"


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
    for c in s.select("div.investment-card"):
        a = c.select_one("a[href]")
        divs = [txt(d) for d in a.find_all("div", recursive=False)] if a else []
        divs = [d for d in divs if d]
        if len(divs) < 2:
            continue
        badge = txt(c.select_one(".absolute.bottom-5"))
        nm, desc = divs[-2], divs[-1]
        if badge and nm == badge:
            continue
        if nm.lower() in seen:
            continue
        seen.add(nm.lower())
        out.append(rec(nm, desc, None, PRIMARY, SOURCE_URL, scraped_at, portfolio_status=badge,
                       status="exited" if badge and re.search(r"realized|exit", badge, re.I) else None, detail_url=a.get("href")))
    finish(out, "stripes", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
