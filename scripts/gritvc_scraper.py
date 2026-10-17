#!/usr/bin/env python3
"""Grit Capital Partners portfolio scraper -> gritvc_companies.json
Source: https://www.grit.vc/portfolio — portfolio popups: company name (h2), category,
website ('see the website'), 'About' description, year since and exited flag."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.grit.vc/portfolio"
PRIMARY = "Grit Capital Partners"


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
    hs = s.select("h2.is-portfolio")
    for i, h in enumerate(hs):
        nm = txt(h)
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        stop = hs[i + 1] if i + 1 < len(hs) else None
        strs, url = [], None
        for el in h.find_all_next(string=True):
            if stop is not None and el.find_parent() is stop:
                break
            v = clean(el)
            if v:
                strs.append(v)
            if len(strs) > 14:
                break
        for a in h.find_all_next("a", href=True, limit=6):
            if "see the website" in (txt(a) or "").lower():
                url = site(a); break
        d = strs[strs.index("About") + 1] if "About" in strs and strs.index("About") + 1 < len(strs) else None
        yr = strs[strs.index("Since") + 1] if "Since" in strs and strs.index("Since") + 1 < len(strs) else None
        cat = next((x for x in strs[1:4] if x != nm and x.lower() != "see the website"), None)
        if cat in ("About", "Since"):
            cat = None
        out.append(rec(nm, d, url, PRIMARY, SOURCE_URL, scraped_at, category=cat, year=year_of(yr or ""),
                       status="exited" if "Exited" in strs[:12] else None))
    finish(out, "gritvc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
