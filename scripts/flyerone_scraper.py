#!/usr/bin/env python3
"""Flyer One Ventures portfolio scraper -> flyerone_companies.json
Source: https://flyerone.vc/portfolio — portfolio table: company name, industry,
description, model and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://flyerone.vc/portfolio"
PRIMARY = "Flyer One Ventures"


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
    for tr in s.select("tr"):
        tds = tr.find_all("td")
        t = tr.select_one("td.title")
        nm = txt(t)
        st = None
        if nm:
            m = re.search(r"\s*\(((?:acquired|exited)[^)]*)\)\s*$", nm, re.I)
            if m:
                st = clean(m.group(1)); nm = nm[:m.start()]
            nm = clean(re.sub(r"^[^\w(]+", "", nm))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        sel = [txt(x) for x in tr.select("td.select")]
        d = txt(tr.select_one("td.text"))
        u = tr.select_one("td.url a[href]")
        out.append(rec(nm, d, u["href"] if u else None, PRIMARY, SOURCE_URL, scraped_at, sector=sel[0] if sel else None, status=st))
    finish(out, "flyerone", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
