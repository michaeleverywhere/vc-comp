#!/usr/bin/env python3
"""Unruly Capital portfolio scraper -> unrulycapital_companies.json
Source: https://unrulycap.com/ — homepage deal log (`div.deal`): company name,
investment amount, date, one-line description, sectors, country and fund."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://unrulycap.com/"
PRIMARY = "Unruly Capital"


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
    for it in s.select("div.deal"):
        nm = txt(it.select_one("strong"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        meta = [clean(x) for x in (txt(it.select_one("span.meta")) or "").split("·")]
        meta = [x for x in meta if x]
        d = meta[1] if len(meta) > 1 else None
        fund = meta[-1] if len(meta) > 2 and re.match(r"^Fund\b", meta[-1]) else None
        rest = meta[2:-1] if fund else meta[2:]
        sec = [clean(x) for x in rest[0].split(",") if clean(x)] if len(rest) >= 2 else []
        ctry = rest[-1] if rest else None
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at, sectors=sec, amount=txt(it.select_one("span.amount")),
                       date=meta[0] if meta else None, country=ctry,
                       fund=fund))
    finish(out, "unrulycapital", ("description", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
