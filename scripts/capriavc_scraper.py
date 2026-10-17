#!/usr/bin/env python3
"""Capria Ventures portfolio scraper -> capriavc_companies.json
Source: https://capria.vc/entire-portfolio/ — entire-portfolio cards: company name, one-line
description, sector, region, country, investing partner and round."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://capria.vc/entire-portfolio/"
PRIMARY = "Capria Ventures"


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
    for c in s.select("div.pp-wrapper-link"):
        ss = [clean(x) for x in c.stripped_strings if clean(x) and clean(x) != ","]
        if len(ss) < 2:
            continue
        nm = ss[0]
        if nm.lower() in seen:
            continue
        seen.add(nm.lower())
        f = {}
        for k in ("Sector", "Region", "Country", "Investing Partner", "Venture Round"):
            if k in ss:
                i = ss.index(k)
                if i + 1 < len(ss):
                    f[k] = ss[i + 1]
        d = ss[1] if ss[1] not in ("Sector",) else None
        out.append(rec(nm, d, None, PRIMARY, SOURCE_URL, scraped_at, sector=f.get("Sector"), region=f.get("Region"),
                       country=f.get("Country"), investing_partner=f.get("Investing Partner"), round=f.get("Venture Round")))
    finish(out, "capriavc", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
