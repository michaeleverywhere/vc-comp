#!/usr/bin/env python3
"""Oak Investment Partners portfolio scraper -> oak_companies.json
Source: https://www.oakvc.com/investments/ — WordPress investments grid; each `a.investment` opens
a modal (`#<slug>`) with status (Active/Acquired/Public/...), sector, website
and description."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.oakvc.com/investments/"
PRIMARY = "Oak Investment Partners"


def txt(el):
    return clean(el.get_text(" ", strip=True)) if el else None


def site(a):
    h = (a.get("href") or "").strip() if a else ""
    return h if h.startswith("http") and not is_social(h) else None


def soup_of(url):
    s = BeautifulSoup(fetch(url), "html.parser")
    for e in s.select(".w-condition-invisible"):
        e.decompose()
    return s


def main():
    scraped_at = datetime.now(timezone.utc).isoformat()
    out = []
    s = soup_of(SOURCE_URL)
    for a in s.select("a.investment[data-target]"):
        nm = txt(a.select_one(".title"))
        if not nm:
            continue
        m = s.find("div", id=a["data-target"].lstrip("#"), class_="modal")
        f, web, desc, det = {}, None, None, None
        if m:
            for p in m.select(".modal-header p"):
                k = txt(p.find("strong"))
                if k:
                    f[k.rstrip(":").lower()] = clean(p.get_text(" ", strip=True)[len(k):])
                    if k.startswith("URL"):
                        web = site(p.find("a"))
            desc = txt(m.select_one(".modal-body p"))
            d = m.select_one(".modal-header a[href*='/investments/']")
            det = d["href"] if d else None
        st = f.get("status")
        out.append(rec(nm, desc, web, PRIMARY, SOURCE_URL, scraped_at, sectors=[f["sector"]] if f.get("sector") else [],
                       portfolio_status=st, status={"acquired": "acquired", "public": "public", "active": "active"}.get((st or "").lower()),
                       detail_url=det))
    finish(out, "oak", ("description", "company_url", "status", "everywhere_tags"))


if __name__ == "__main__":
    main()
