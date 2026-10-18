#!/usr/bin/env python3
"""1818 Venture Capital portfolio scraper -> 1818venturecapital_companies.json
Source: https://1818venturecapital.com/our-portfolio — portfolio page: company name (site-authored
heading/label text) and website where linked."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://1818venturecapital.com/our-portfolio"
PRIMARY = "1818 Venture Capital"


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
    for el in s.select('div.portfolio_list-item-company-name'):
        nm = clean(re.sub(r"(?i)\s*logo\s*$", "", txt(el) or ""))
        if not nm or len(nm) > 60 or len(nm.split()) > 5 or nm.lower() in seen or re.compile('^$', re.I).search(nm):
            continue
        a = el if el.name == "a" else (el.find_parent("a", href=re.compile(r"^https?://")) or el.find("a", href=re.compile(r"^https?://")))
        u = a["href"] if a is not None and a.get("href", "").startswith("http") and '1818venturecapital' not in a["href"] and not re.search(r"linkedin|twitter|x\.com/|crunchbase|facebook|instagram", a["href"]) else None
        st = None
        m = re.compile('(?!x)x', re.I).search(nm)
        if m:
            st = clean(m.group(1)); nm = clean(nm[:m.start()])
            if not nm or nm.lower() in seen:
                continue
        seen.add(nm.lower())
        out.append(rec(nm, None, u, PRIMARY, SOURCE_URL, scraped_at, status=st))
    # _POSTFIX_ site-authored names: trim decoration / drop non-company strings
    finish(out, "1818venturecapital", ("company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
