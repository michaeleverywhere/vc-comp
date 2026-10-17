#!/usr/bin/env python3
"""Chamaeleon portfolio scraper -> chamaeleon_companies.json
Source: https://www.chamaeleon.vc/portfolio — Next.js portfolio page: current
company boxes (name from logo alt, status line such as 'Sold Sensor Tower') and
the 'prior investments' logo wall (site-authored logo alt text)."""
import os, re, sys, json
from datetime import datetime, timezone
from urllib.parse import urljoin
from bs4 import BeautifulSoup

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _scraper_common import fetch_response, fetch_many, clean, is_social, year_of
from _d50_common import rec, finish

SOURCE_URL = "https://www.chamaeleon.vc/portfolio"
PRIMARY = "Chamaeleon"


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
    for img in s.select("img[alt]"):
        nm = clean(re.sub(r"\s*logo$", "", img.get("alt") or "", flags=re.I))
        if not nm or nm.lower() in seen or nm.lower() in ("chamaeleon", "megaphone illustration") or "illustration" in nm.lower():
            continue
        box = img.find_parent(class_=re.compile("company-box_companyBox"))
        st = txt(box.select_one("[class*=company-box_status]")) if box else None
        seen.add(nm.lower())
        out.append(rec(nm, None, None, PRIMARY, SOURCE_URL, scraped_at, portfolio_status=st,
                       status="acquired" if st and re.search(r"sold|acquired", st, re.I) else None))
    finish(out, "chamaeleon", ("everywhere_tags",))


if __name__ == "__main__":
    main()
