#!/usr/bin/env python3
"""Porsche Ventures portfolio scraper -> porscheventures_companies.json
Source: https://porsche.ventures/portfolio — Portfolio grid: company name (site logo alt),
region, status, sectors, short description and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://porsche.ventures/portfolio"
PRIMARY = "Porsche Ventures"


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
    for it in s.select("div.portfolio__items__item"):
        img = it.select_one("img[alt]")
        nm = clean(re.sub(r"\s*logo$", "", img.get("alt") or "", flags=re.I)) if img else None
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        p = [clean(x) for x in it.stripped_strings if clean(x)]
        a = it.select_one("a[href^=http]")
        st = it.get("data-status")
        out.append(rec(nm, p[1] if len(p) > 1 else None, site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       location=(it.get("data-region") or "").upper() or None, portfolio_status=st,
                       sectors=[x for x in (it.get("data-sectors") or "").split() if x],
                       status="exited" if st and "exit" in st.lower() else None))
    finish(out, "porscheventures", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
