#!/usr/bin/env python3
"""UTEC (University of Tokyo Edge Capital Partners) portfolio scraper -> utecvc_companies.json
Source: https://www.ut-ec.co.jp/english/our_companies/ — 'Our Companies' list (`li.box_link`):
company name, profile link, sector category, UTEC fund and exit status. Entries
categorised 'fund' (fund LP commitments) are excluded."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.ut-ec.co.jp/english/our_companies/"
PRIMARY = "UTEC (University of Tokyo Edge Capital Partners)"


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
    for li in s.select("li.box_link"):
        if (li.get("data-cat") or "").strip().lower() == "fund":
            continue
        a = li.select_one("dl.info dt a")
        nm = txt(a)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        st = (li.get("data-status") or "").strip()
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, profile_url=a.get("href"),
                       sector=clean(li.get("data-cat")) or None, fund=clean(li.get("data-fund")) or None,
                       exit_status=None if st in ("", "none") else st))
    finish(out, "utecvc", ("everywhere_tags",))


if __name__ == "__main__":
    main()
