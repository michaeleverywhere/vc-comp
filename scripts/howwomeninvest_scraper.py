#!/usr/bin/env python3
"""How Women Invest portfolio scraper -> howwomeninvest_companies.json
Source: https://www.howwomeninvest.com/portfolio — Wix repeater: company name,
Exited marker and category."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.howwomeninvest.com/portfolio"
PRIMARY = "How Women Invest"


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
    for it in s.select(".wixui-repeater__item"):
        parts = [txt(x) for x in it.select("h4") if txt(x)]
        if not parts or len(it.select("h4.font_4")) == 0:
            continue
        nm = parts[0]
        ex = "Exited" in parts[1:]
        cat = None
        if "•" in parts:
            i = parts.index("•")
            cat = parts[i + 1] if i + 1 < len(parts) else None
        if not nm or nm in ("•", "Exited"):
            continue
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, sectors=[cat] if cat else [], status="exited" if ex else None))
    finish(out, "howwomeninvest", ("everywhere_tags",))


if __name__ == "__main__":
    main()
