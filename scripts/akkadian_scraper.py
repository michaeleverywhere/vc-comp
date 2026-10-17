#!/usr/bin/env python3
"""Akkadian Ventures portfolio scraper -> akkadian_companies.json
Source: https://akkadian.vc/portfolio — portfolio cards: company name (h3), one-line
description, status (e.g. IPO / Acquired) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://akkadian.vc/portfolio"
PRIMARY = "Akkadian Ventures"


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
    for a in s.select("a[href^='http']"):
        h = a.find("h3")
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        ss = [clean(x) for x in a.stripped_strings if clean(x) and clean(x) != nm]
        d = next((x for x in ss if len(x) > 15), None)
        st = next((x for x in ss if re.match(r"(?i)^(ipo|acquired|exited|m&a)", x)), None)
        out.append(rec(nm, d, site(a), PRIMARY, SOURCE_URL, scraped_at, status="exited" if st else None, exit_note=st))
    finish(out, "akkadian", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
