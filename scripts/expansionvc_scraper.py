#!/usr/bin/env python3
"""Expansion VC portfolio scraper -> expansionvc_companies.json
Source: https://www.expansionvc.com/portfolio — Webflow portfolio grid: company name,
one-line description, website, category filters and acquired badge."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.expansionvc.com/portfolio"
PRIMARY = "Expansion VC"


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
    for it in s.select("div.logotip-item"):
        nm = txt(it.select_one(".logotip-title"))
        if not nm:
            continue
        cats = [txt(x) for x in it.select(".logotip-filter .w-dyn-item") if txt(x)]
        badge = txt(it.select_one(".logotip-description"))
        exited = bool(badge and re.search(r"acqui|exit|ipo", badge, re.I)) or "EXITS" in cats
        out.append(rec(nm, txt(it.select_one(".logotip-desc")), site(it.select_one("a.logotip-link")), PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[c.title() if c.isupper() and len(c) > 4 else c for c in cats if c not in ("ALL", "EXITS")],
                       exit_note=badge, status="exited" if exited else None))
    finish(out, "expansionvc", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
