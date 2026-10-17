#!/usr/bin/env python3
"""Earthshot Ventures portfolio scraper -> earthshotvc_companies.json
Source: https://earthshot.vc/companies — companies table: company name, sector and
website (featured cards add a one-line description)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://earthshot.vc/companies"
PRIMARY = "Earthshot Ventures"


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
    seen = {}
    for it in s.select("div.table6_item"):
        nm = txt(it.select_one(".table6_text-title"))
        if not nm or nm.lower() in seen:
            continue
        a = it.find_parent("a", href=re.compile(r"^https?://")) or it.find("a", href=re.compile(r"^https?://"))
        r = rec(nm, None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at, sector=txt(it.select_one(".table6_tab-2")))
        seen[nm.lower()] = r
        out.append(r)
    for a in s.select("a.portfolio12_item-link"):
        ss = [clean(x) for x in a.stripped_strings if clean(x)]
        if ss and ss[0].lower() not in seen:
            seen[ss[0].lower()] = 1
            out.append(rec(ss[0], ss[1] if len(ss) > 2 else None, site(a), PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "earthshotvc", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
