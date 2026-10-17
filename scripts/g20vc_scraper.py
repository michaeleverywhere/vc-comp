#!/usr/bin/env python3
"""G20 Ventures portfolio scraper -> g20vc_companies.json
Source: https://www.g20vc.com/portfolio — portfolio page 'Here's who we're
behind so far': company name (h3), opening description paragraph and website
('Learn more' link)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.g20vc.com/portfolio"
PRIMARY = "G20 Ventures"


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
    for h in s.select("h3"):
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        url = None
        for a in h.find_all_next("a", href=True):
            nh = a.find_previous("h3")
            if nh is not h:
                break
            if "learn more" in (txt(a) or "").lower():
                url = site(a); break
        if not url:
            continue
        seen.add(nm.lower())
        p = h.find_next("p")
        d = txt(p) if p and p.find_previous("h3") is h else None
        out.append(rec(nm, d, url, PRIMARY, SOURCE_URL, scraped_at))
    finish(out, "g20vc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
