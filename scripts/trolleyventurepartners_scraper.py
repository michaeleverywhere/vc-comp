#!/usr/bin/env python3
"""Trolley Ventures portfolio scraper -> trolleyventurepartners_companies.json
Source: https://trolleyventures.com/our-portfolio — portfolio page: company name (site-authored
heading/label text) and website where linked."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://trolleyventures.com/our-portfolio"
PRIMARY = "Trolley Ventures"


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
    for el in s.select('h4.x-el.x-el-h4.c1-1.c1-2.c1-22.c1-23.c1-6q.c1-2v.c1-2w.c1-1c.c1-1e.c1-b.c1-74.c1-59.c1-3i.c1-5a.c1-5c.c1-5d.c1-5e'):
        nm = clean(re.sub(r"(?i)\s*logo\s*$", "", txt(el) or ""))
        if not nm or len(nm) > 60 or len(nm.split()) > 5 or nm.lower() in seen or re.compile('^$', re.I).search(nm):
            continue
        a = el if el.name == "a" else (el.find_parent("a", href=re.compile(r"^https?://")) or el.find("a", href=re.compile(r"^https?://")))
        u = a["href"] if a is not None and a.get("href", "").startswith("http") and 'trolleyventures' not in a["href"] and not re.search(r"linkedin|twitter|x\.com/|crunchbase|facebook|instagram", a["href"]) else None
        st = None
        m = re.compile('(?!x)x', re.I).search(nm)
        if m:
            st = clean(m.group(1)); nm = clean(nm[:m.start()])
            if not nm or nm.lower() in seen:
                continue
        seen.add(nm.lower())
        out.append(rec(nm, None, u, PRIMARY, SOURCE_URL, scraped_at, status=st))
    # _POSTFIX_ site-authored names: trim decoration / drop non-company strings
    out = [r for r in out if r["company_name"]]
    _s = set(); out = [r for r in out if not (r["company_name"].lower() in _s or _s.add(r["company_name"].lower()))]
    finish(out, "trolleyventurepartners", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
