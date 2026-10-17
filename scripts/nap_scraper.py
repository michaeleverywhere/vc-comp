#!/usr/bin/env python3
"""NAP portfolio scraper -> nap_companies.json
Source: https://nap.vc/build/companies — Companies table: company name, sector, location and
website; exited companies flagged."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://nap.vc/build/companies"
PRIMARY = "NAP"


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
    for e in s.select(".portfolio-name"):
        nm = clean(e.get_text(" ", strip=True).replace("\u2197", ""))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ex = "portfolio-name-exit" in (e.get("class") or [])
        sec = loc = None
        sib = [clean(x.get_text(" ", strip=True)) for x in e.find_next_siblings(limit=2)] if not ex else []
        if len(sib) == 2 and sib[0] and not sib[0].endswith("\u2197"):
            sec, loc = sib
        out.append(rec(nm, None, site(e) if e.name == "a" else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[sec] if sec else [], location=loc, status="exited" if ex else None))
    finish(out, "nap", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
