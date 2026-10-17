#!/usr/bin/env python3
"""TRIVE VC portfolio scraper -> trive_companies.json
Source: https://trive.vc/ — Portfolio cards: company name, industry, description,
fund, status and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://trive.vc/"
PRIMARY = "TRIVE VC"


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
    for c in s.select("div.p-card[data-name]"):
        nm = clean(c.get("data-name"))
        if not nm or nm.lower() in seen:
            continue
        seen.add(nm.lower())
        a = c.select_one("a[href^=http]")
        p = [clean(x) for x in c.stripped_strings]
        st = c.get("data-status")
        out.append(rec(nm, clean(c.get("data-desc")), site(a) if a else None, PRIMARY, SOURCE_URL, scraped_at,
                       sectors=[clean(c.get("data-industry"))] if c.get("data-industry") else [], fund=p[-1] if p and "TRIVE" in p[-1] else None,
                       portfolio_status=st, status="exited" if st and st.lower() in ("exited", "exit", "acquired") else None))
    finish(out, "trive", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
