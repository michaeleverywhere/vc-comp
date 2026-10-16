#!/usr/bin/env python3
"""Zetta Ventures portfolio scraper -> zetta_companies.json
Source: https://www.zettavp.com/companies — Next.js page; the embedded __NEXT_DATA__ companies grid
(Sanity CMS) lists company name, short description and slug (detail page
/companies/<slug>)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.zettavp.com/companies"
PRIMARY = "Zetta Ventures"


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
    html = fetch(SOURCE_URL)
    m = re.search(r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    data = json.loads(m.group(1)) if m else {}
    comps = []
    def walk(o):
        if isinstance(o, dict):
            if isinstance(o.get("allCompanies"), list):
                comps.extend(o["allCompanies"])
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(data.get("props", {}))
    for c in comps:
        nm = clean(c.get("name"))
        if not nm:
            continue
        slug = (c.get("slug") or {}).get("current")
        out.append(rec(nm, clean(c.get("descriptionShort")), None, PRIMARY, SOURCE_URL, scraped_at,
                       detail_url=f"https://www.zettavp.com/companies/{slug}" if slug else None))
    finish(out, "zetta", ("description", "everywhere_tags"))


if __name__ == "__main__":
    main()
