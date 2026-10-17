#!/usr/bin/env python3
"""Refract Ventures portfolio scraper -> refract_companies.json
Source: https://www.refract.vc/ — homepage 'Investors in' paragraph: company names
with websites and acquisition notes (acquirer)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.refract.vc/"
PRIMARY = "Refract Ventures"


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
    p = next((x.find_next("p") for x in s.find_all("p") if (txt(x) or "").startswith("Investors in")), None)
    last = None
    for a in (p.find_all("a") if p else []):
        prev = a.previous_sibling
        if isinstance(prev, str) and "acquired by" in prev.lower() and last is not None:
            acq = clean((txt(a) or "").rstrip(")"))
            last["status"] = "acquired"
            last["exit_note"] = f"Acquired by {acq}" if acq else None
            continue
        nm = txt(a)
        if not nm:
            continue
        last = rec(nm, None, site(a), PRIMARY, SOURCE_URL, scraped_at, status=None, exit_note=None)
        out.append(last)
    finish(out, "refract",  ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
