#!/usr/bin/env python3
"""Anzu Partners portfolio scraper -> anzu_companies.json
Source: https://www.anzupartners.com/portfolio/ — Filterable portfolio gallery: company name,
description, location, investment date, sector and status filters."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.anzupartners.com/portfolio/"
PRIMARY = "Anzu Partners"


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
    lab = {x.get("data-filter", "").lstrip("."): txt(x) for x in s.select("[data-filter]")}
    seen = set()
    for w in s.select("div.eael-filterable-gallery-item-wrap"):
        nm = txt(w.select_one(".fg-item-title"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ps = [txt(p) for p in w.select(".fg-item-content p") if txt(p)]
        def f(k):
            return next((re.sub(k + r":\s*", "", p) for p in ps if p.startswith(k + ":")), None)
        desc = next((p for p in ps if not re.match(r"(Location|Investment Date):", p)), None)
        cls = [lab[c] for c in w.get("class", []) if c in lab]
        secs = [c for c in cls if c in ("Clean Tech", "Industrial", "Life Sciences")]
        st = [c for c in cls if c not in secs]
        out.append(rec(nm, desc, None, PRIMARY, SOURCE_URL, scraped_at, location=f("Location"), invested_date=f("Investment Date"),
                       sectors=secs, portfolio_status=", ".join(st) or None,
                       status="exited" if any(x in ("Acquired", "Exited", "IPO", "Public Listing", "Merged") for x in st) else None))
    finish(out, "anzu", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
