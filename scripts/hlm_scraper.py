#!/usr/bin/env python3
"""HLM Venture Partners portfolio scraper -> hlm_companies.json
Source: https://www.hlmvp.com/portfolio/ — portfolio postcards: company name,
description, status (Current / Exited) and website."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.hlmvp.com/portfolio/"
PRIMARY = "HLM Venture Partners"


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
    for b in s.select("button.postcards__card"):
        nm = txt(b.select_one(".postcards__card__info__header h2"))
        if not nm:
            continue
        st = None
        h3 = next((h for h in b.select("h3") if "Status" in h.get_text()), None)
        if h3 and h3.find("p"):
            st = txt(h3.find("p"))
        web = next((site(a) for a in b.select("a[href^=http]") if site(a)), None)
        out.append(rec(nm, txt(b.select_one(".postcards__card__info__content")), web, PRIMARY, SOURCE_URL, scraped_at,
                       portfolio_status=st, status="exited" if st and "exit" in st.lower() else None))
    finish(out, "hlm", ("description", "company_url", "everywhere_tags"))


if __name__ == "__main__":
    main()
