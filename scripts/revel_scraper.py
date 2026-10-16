#!/usr/bin/env python3
"""Revel Partners portfolio scraper -> revel_companies.json
Source: https://revelpartners.com/companies — B12 site items grid; each company's lightbox caption
(data-caption) carries name, CEO, location, website and description; the card
subtitle carries exit notes (e.g. 'ACQUIRED BY CLIO: 9/1/21')."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, fetch_response, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://revelpartners.com/companies"
PRIMARY = "Revel Partners"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    # the server omits a charset header, so decode the UTF-8 bytes explicitly
    s = BeautifulSoup(fetch_response(url).content.decode("utf-8", "replace"), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for li in s.select("li.items-grid__item"):
        a = li.select_one("a[data-caption]")
        cap = BeautifulSoup(a["data-caption"], "html.parser") if a else None
        nm = txt(cap.find("h3")) if cap else None
        nm = nm or txt(li.select_one(".items-grid__header"))
        if not nm:
            continue
        f, desc, web = {}, None, None
        if cap:
            for p in cap.find_all("p"):
                k = txt(p.find("strong"))
                if k:
                    f[k.rstrip(":").lower()] = clean(p.get_text(" ", strip=True)[len(k):])
                    if k.startswith("WEBSITE"):
                        web = site(p.find("a"))
                elif txt(p):
                    desc = txt(p)
        content = li.select_one(".items-grid__item-content")
        sub = list(content.stripped_strings)[1:2] if content else []
        note = clean(sub[0]) if sub and sub[0] != "Learn more" else None
        out.append(rec(nm, desc, web, PRIMARY, SOURCE_URL, scraped_at, location=f.get("location"), ceo=f.get("ceo"),
                       exit_note=note, status="acquired" if note and "acquired" in note.lower() else None))
    finish(out, "revel", ("description", "company_url", "location", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
