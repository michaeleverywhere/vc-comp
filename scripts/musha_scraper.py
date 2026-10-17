#!/usr/bin/env python3
"""Musha Ventures portfolio scraper -> musha_companies.json
Source: https://mushaventures.com/ — homepage portfolio logo wall: company name (logo alt
text, "logo" suffix removed), country, year and status badge."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://mushaventures.com/"
PRIMARY = "Musha Ventures"


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
    for b in s.select("button.logo-tile"):
        img = b.select_one("img[alt]")
        nm = clean(re.sub(r"\s+logo$", "", img.get("alt") or "", flags=re.I)) if img else None
        if not nm:
            continue
        sp = [txt(x) for x in b.select(".logo-tile-copy small span") if txt(x)]
        st = txt(b.select_one(".logo-tile-status"))
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at,
                       location=sp[0] if sp else None, vintage_year=next((x for x in sp if re.fullmatch(r"\d{4}", x)), None),
                       portfolio_status=st, status="exited" if st and re.search(r"exit|acqui", st, re.I) else None))
    finish(out, "musha", ("everywhere_tags",))


if __name__ == "__main__":
    main()
