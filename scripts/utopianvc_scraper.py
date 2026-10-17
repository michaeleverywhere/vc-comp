#!/usr/bin/env python3
"""Utopian Ventures portfolio scraper -> utopianvc_companies.json
Source: https://utopian.vc/portfolio/ — portfolio table: company name, status flag
(IPO / listed / acquired), description, entry stage and year, website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://utopian.vc/portfolio/"
PRIMARY = "Utopian Ventures"


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
    for a in s.select("a.row"):
        nm = txt(a.select_one("h3.name"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in a.stripped_strings if clean(x) and clean(x) != nm]
        flags = a.get("data-flags") or ""
        d = next((x for x in ss if len(x) > 30), None)
        yr = next((x for x in ss if re.fullmatch(r"(19|20)\d\d", x)), None)
        ex = bool(re.search(r"ipo|acqui|exit|listed", flags, re.I))
        out.append(rec(nm, d, site(a) if a.get("href", "").startswith("http") else None, PRIMARY, SOURCE_URL, scraped_at,
                       status="exited" if ex else None, flags=flags or None, year=int(yr) if yr else None))
    finish(out, "utopianvc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
