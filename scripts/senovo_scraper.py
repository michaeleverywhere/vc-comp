#!/usr/bin/env python3
"""Senovo portfolio scraper -> senovo_companies.json
Source: https://senovo.vc/portfolio/ — Portfolio grid: company name, tagline, year,
locations, founders and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://senovo.vc/portfolio/"
PRIMARY = "Senovo"


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
    for h in s.select("h2.name"):
        box = h.find_parent(class_="logo")
        nm = txt(h)
        if not box or not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in box.stripped_strings if clean(x) and clean(x) not in ("LinkedIn", "Twitter", "www")]
        i = p.index(nm) if nm in p else 0
        r = p[i + 1:]
        yr = r[1] if len(r) > 1 and re.fullmatch(r"\d{4}", r[1]) else None
        a = [x for x in box.select("a[href^=http]") if not re.search(r"linkedin|twitter|x\.com|facebook|instagram", x["href"])]
        out.append(rec(nm, r[0] if r else None, site(a[0]) if a else None, PRIMARY, SOURCE_URL, scraped_at, year=yr,
                       location=r[2] if yr and len(r) > 2 else None))
    finish(out, "senovo", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
