#!/usr/bin/env python3
"""Trucks VC portfolio scraper -> trucks_companies.json
Source: https://www.trucks.vc/portfolio — Webflow CMS portfolio rows: company name
(exit notes such as '(NASDAQ: LIDR)' split out), focus line, website and a
'Learn More' press link."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.trucks.vc/portfolio"
PRIMARY = "Trucks VC"


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
    for it in s.select(".w-dyn-item"):
        a = it.select_one("a.company-name")
        raw = txt(a)
        if not raw:
            continue
        m = re.match(r"^(.*?)\s*\(([^)]*)\)\s*$", raw)
        nm, note = (clean(m.group(1)), clean(m.group(2))) if m else (raw, None)
        lm = it.select_one("a.button-learn-more")
        out.append(rec(nm, txt(it.select_one(".focus")), site(a), PRIMARY, SOURCE_URL, scraped_at, exit_note=note,
                       learn_more_url=lm.get("href") if lm else None,
                       status=("acquired" if note and note.lower().startswith("acq") else
                               ("public" if note and re.search(r"NASDAQ|NYSE", note) else None))))
    finish(out, "trucks", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
