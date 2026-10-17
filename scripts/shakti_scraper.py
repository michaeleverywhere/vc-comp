#!/usr/bin/env python3
"""SHAKTI portfolio scraper -> shakti_companies.json
Source: https://shaktivc.com/companies — portfolio table (`tr.hover-color`): company
name, description, sector, year and stage of investment, SHAKTI fund and
detail page."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://shaktivc.com/companies"
PRIMARY = "SHAKTI"


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
    for tr in s.select("tr.hover-color"):
        nm = txt(tr.select_one("h2.visually-hidden"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        td = tr.find_all("td", recursive=False)
        g = lambda i: txt(td[i]) if len(td) > i else None
        yr = g(3) or ""
        m = re.match(r"^(\d{4})\s*(?:\((.*)\))?", yr)
        a = tr.select_one("a[href]")
        sec = g(2)
        out.append(rec(nm, g(1), None, PRIMARY, SOURCE_URL, scraped_at, sectors=[sec] if sec else [],
                       year_invested=int(m.group(1)) if m else None, stage=m.group(2) if m and m.group(2) else None,
                       fund=g(4), detail_url=urljoin(SOURCE_URL, a["href"]) if a else None))
    finish(out, "shakti", ("description", "fund", "everywhere_tags"))


if __name__ == "__main__":
    main()
