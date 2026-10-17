#!/usr/bin/env python3
"""Twine Ventures portfolio scraper -> twinevc_companies.json
Source: https://www.twineventures.com/ — homepage portfolio list: company name (h3),
one-line description, sector and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.twineventures.com/"
PRIMARY = "Twine Ventures"


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
    for a in s.select("a.portfolio--item__link"):
        nm = txt(a.select_one("h3"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in a.stripped_strings if clean(x) and clean(x) != nm]
        acq = bool(re.search(r"\(acq\)\s*$", nm))
        nm = clean(re.sub(r"\s*\(acq\)\s*$", "", nm))
        out.append(rec(nm, ss[0] if ss else None, site(a), PRIMARY, SOURCE_URL, scraped_at, status="exited" if acq else None))
    finish(out, "twinevc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
